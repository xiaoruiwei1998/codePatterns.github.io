
// click each test case
$(":button").click(function(){clickTestCase(this)});

function clickTestCase(node) {
    let test_case_regex = /%28(\d)+%29/;
    let new_test_case = "%28" + $(node).html().replace("(","%28").replace(")","%29").split("%28")[1];
    let stu_src = $("#python-tutor-frame").attr("src").replace(test_case_regex, new_test_case);
    $("#python-tutor-frame").attr("src", stu_src);
  
    let cor_src = $("#python-tutor-frame-correct").attr("src").replace(test_case_regex, new_test_case);
    $("#python-tutor-frame-correct").attr("src", cor_src);
  }