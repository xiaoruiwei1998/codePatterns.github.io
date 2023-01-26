function createCodeHistorySnapshots (codeHistory) {

    // mark the largest edit distance and use it as 
    let max_edit_dist = 0;
    for (let i=0; i<codeHistory.length; i++) {
      if (parseInt(codeHistory[i]['edit_dist']) > max_edit_dist) {
        max_edit_dist = parseInt(codeHistory[i]['edit_dist']);
      }
    }
    max_edit_dist *= 1.2;

    for (let i=0; i<codeHistory.length; i++) {
      let card_id = "snapshot_"+i;
      let card_class = "card";

      // one snapshot of correction history
      let card_content = codeHistory[i]['correction_history'];
      if (card_content.includes("Syntax Error"))
        card_class = "card syntax_error";
      let card_correction = $("<div class=\"col-lg-6 mb-4\"><div class=\""+card_class+"\" id=\""+card_id+"\"><div class=\"card-body\"><p class=\"card-text\">"+card_content+"</p></div></div></div>");
      $("#code-history-snapshot").append(card_correction);

      // one snapshot of student edit history 
      card_content = codeHistory[i]['student_history'];
      let card_student = $("<div class=\"col-lg-6 mb-4\" id=\"infoi\"><div class=\""+card_class+"\" id=\""+card_id+"\"><div class=\"card-body\"><p class=\"card-text\">"+card_content+"</p></div></div></div>");
      $("#student-edits").append(card_student);

      // one snapshot of edit distance
      card_class = "card dist_card";
      let correctness_percentile = 1 - codeHistory[i]['edit_dist']/max_edit_dist;
      if (codeHistory[i]['edit_dist']<0)
        correctness_percentile = 0;
      console.log(correctness_percentile*$(".col-lg-6").width());
      let card_dist = $("<div class=\"col-lg-6 mb-4\"><div class=\""+card_class+"\" style=\"background-color:LightGray;\"><div class=\"card-body\"><p style=\"text-align: center; font-size: 10px\">"+codeHistory[i]['edit_dist']+" edits away</p></div></div></div>");
      let dist_color_bar = $("<div class=\"card\" style=\"background-color:darkgreen;opacity:60%;height: 18.9px;\"></div>")
      .width(correctness_percentile*$(".col-lg-6").width())
      .height($(".dist_card").height()*0.9)
      .css({position: "absolute"})
      .css({top: "-10.5px"})
      .css({left: 1+$(".col-lg-6").width()*i});
      $("#distance-to-correct-answer").append(card_dist);
      $("#distance-to-correct-answer").append(dist_color_bar);
      // or say XX edits away?

      // load the main view of this snapshot
      $("div#"+card_id+".card").click(function(){clickSnapshot(card_id, codeHistory[i]);});
    }
    
    // show checked code history
    clickcheckbox();
    
}


function setSnapshotCSS (syntax_error_color="rgb(240, 240, 240)", correct_color="rgb(240, 240, 240)", student_edit_color="rgb(145, 202, 252)", correction_edit_color="rgb(252, 230, 145)") {
    // set sytax error snapshot to gray
    $(".syntax_error").css("background", syntax_error_color);
    $(".correction-node.ast-node").css("background", correct_color);
    $(".correction-node.ast-node").css("color", correct_color);
    $(".student-node.ast-node").css("background", correct_color);
    $(".student-node.ast-node").css("color", correct_color);

    // set correction's edits to yellow
    $(".correction-node.ast-node.insert-node").css("background", correction_edit_color);
    $(".correction-node.ast-node.rename-node").css("background", correction_edit_color);
    $(".correction-node.ast-node.move-node").css("background", correction_edit_color);
    $(".correction-node.ast-node.delete-node").css("background", correction_edit_color);
    $(".correction-node.ast-node.insert-node").css("color", correction_edit_color);
    $(".correction-node.ast-node.rename-node").css("color", correction_edit_color);
    $(".correction-node.ast-node.move-node").css("color", correction_edit_color);
    $(".correction-node.ast-node.delete-node").css("color", correction_edit_color);

    // set student's edits to blue
    $(".student-node.ast-node.insert-node").css("background", student_edit_color);
    $(".student-node.ast-node.rename-node").css("background", student_edit_color);
    $(".student-node.ast-node.move-node").css("background", student_edit_color);
    $(".student-node.ast-node.delete-node").css("background", student_edit_color);
    $(".student-node.ast-node.insert-node").css("color", student_edit_color);
    $(".student-node.ast-node.rename-node").css("color", student_edit_color);
    $(".student-node.ast-node.move-node").css("color", student_edit_color);
    $(".student-node.ast-node.delete-node").css("color", student_edit_color);
}

function clickSnapshot(card_id, card_content) {
  $(".card").css('border', '');
  $("div#"+card_id+".card").css('border', '3px solid gray');
  $("#one-snapshot").html(card_content['correction_history']);
  $("#one-snapshot").find(".ast-node").css("color", "black");
  $("#one-snapshot").find(".ast-node").css("background", "#ebebeb");
  bugsTracing(card_content);
  
}

function clickcheckbox() {
  // all checked
  if ($("#stu-checkbox").is(':checked') && $("#cor-checkbox").is(':checked')) {
    setSnapshotCSS (syntax_error_color="rgb(240, 240, 240)", correct_color="rgb(240, 240, 240)", student_edit_color="navy", correction_edit_color="red");
    $("#code-history-snapshot").show();
    $("#student-edits").show();
  }
  
  // only student's
  else if ($("#stu-checkbox").is(':checked') && !$("#cor-checkbox").is(':checked')){
    setSnapshotCSS (syntax_error_color="rgb(240, 240, 240)", correct_color="rgb(240, 240, 240)", student_edit_color="navy", correction_edit_color="red");
    $("#code-history-snapshot").hide();
    $("#student-edits").show();
  }
  
  // only correction's
  else if (!$("#stu-checkbox").is(':checked') && $("#cor-checkbox").is(':checked')) {
    setSnapshotCSS (syntax_error_color="rgb(240, 240, 240)", correct_color="rgb(240, 240, 240)", student_edit_color="navy", correction_edit_color="red");
    $("#student-edits").hide();
    $("#code-history-snapshot").show();
  }
  
  // none of them selected 
  else {
    setSnapshotCSS (syntax_error_color="rgb(240, 240, 240)", correct_color="rgb(240, 240, 240)", student_edit_color="rgb(240, 240, 240)", correction_edit_color="rgb(240, 240, 240)");
  }
}

// change snapshot highlights when checkbox changes
$(".form-check-input").click(function(){clickcheckbox()});