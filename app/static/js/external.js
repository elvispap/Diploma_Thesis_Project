$(document).ready(function() {

	$(".citation_clicked").click(function(){
		console.log("cit");
        $(this).parent().next(".cited_publications_div").slideToggle();
        

    });


});