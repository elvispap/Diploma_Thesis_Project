$(document).ready(function() {

    jQuery.expr[':'].Contains = function(a, i, m) {
        return jQuery(a).text().toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
    };
    $('#search_publication_cited').on('keyup', function() {
        console.log("aaa");
        var value = $(this).val();
        if (value) {
            $('#publications_cited_ul li').hide();
            $('#publications_cited_ul li:Contains('+value+')').show();
        } else {
            $('#publications_cited_ul li').show();                  
        }
    });
});
