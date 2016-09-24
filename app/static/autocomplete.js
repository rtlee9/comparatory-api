$(function() {
    $("#cname-box").autocomplete({
        source:function(request, response) {
            $.getJSON("/autocomplete",{
                q: request.term, // in flask, "q" will be the argument to look for using request.args
            }, function(data) {
                response(data.matching_results); // matching_results from jsonify
            });
        },
        minLength: 2,
        select: function(event, ui) {
            console.log(ui.item.value); // not in your question, but might help later
        }
    });
})
