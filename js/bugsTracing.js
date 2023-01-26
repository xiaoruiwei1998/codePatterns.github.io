function bugsTracing(card_content) {
    let bugs_col = $("#bugs");
    let changes_col = $("#changes");
    bugs_col.empty();
    changes_col.empty();
    let bugs = card_content['bugs'].split(",");
    let changes = card_content['changes'].split(",");

    for (let i=0; i<bugs.length; i++)
        bugs_col.append("<li> bugs "+bugs[i]+"</li>")
    for (let i=0; i<changes.length; i++)
        changes_col.append("<li> changes "+changes[i]+"</li>")
}