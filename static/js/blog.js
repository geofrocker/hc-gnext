$(document).ready(function() {
    $(".ui.form select").addClass("ui search dropdown");
    $('select.dropdown').dropdown();
    $("#id_content").markdown();
});