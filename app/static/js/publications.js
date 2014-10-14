$(document).ready(function() {


    // $(document).ajaxStart(function () {
    //     $('#loader').shCircleLoader();
    // }).ajaxStop(function () {
    //     $('#loader').shCircleLoader('destroy');
    // });

    $(".citation_clicked").click(function(){
        $(this).parent().next(".cited_publications_div").slideToggle();
    });

    $(".target").tipper({
        direction: "top",
        follow: true,
        
    });
    
    var sampleTags = [];
    $("#keywords_ul li").each(function () {
    	if ($(this).text() != "") {
    		sampleTags.push(String($(this).text()).trim());
    	}
    	
        
    });

    var sampleTags_2 = [];
    $("#authors_ul li").each(function () {
        if ($(this).text() != "") {
            sampleTags_2.push(String($(this).text()).trim());
        }
        
        
    });


   

    var cur_year = new Date().getFullYear();
    var obj = document.getElementById("doc_year_from");
    for (var i = 1969; i <= cur_year; i++)     { 
        if (i == 1969){
            opt = document.createElement("option");
            opt.value = "";
            opt.text="";
            obj.appendChild(opt);   
        }
        else{
            opt = document.createElement("option");
            opt.value = i;
            opt.text=i;
            obj.appendChild(opt);   
        }               
        
    }
    //document.getElementById("doc_year_from").value = "-";

   
    var obj1 = document.getElementById("doc_year_to");
    for (var i = 1969; i <= cur_year; i++)     {                
        if (i == 1969){
            opt = document.createElement("option");
            opt.value = "";
            opt.text="";
            obj1.appendChild(opt);   
        }
        else{
            opt = document.createElement("option");
            opt.value = i;
            opt.text=i;
            obj1.appendChild(opt);   
        }               
    }
    //document.getElementById("doc_year_to").value = "-";

    var eventTags = $('#eventTags');

    var addEvent = function(text) {
        $('#events_container').append(text + '<br>');
    };

    eventTags.tagit({
        availableTags: sampleTags,
        beforeTagAdded: function(evt, ui) {
            if (!ui.duringInitialization) {
                addEvent('beforeTagAdded: ' + eventTags.tagit('tagLabel', ui.tag));
            }
        },
        afterTagAdded: function(evt, ui) {
            if (!ui.duringInitialization) {
                addEvent('afterTagAdded: ' + eventTags.tagit('tagLabel', ui.tag));
            }
        },
        beforeTagRemoved: function(evt, ui) {
            addEvent('beforeTagRemoved: ' + eventTags.tagit('tagLabel', ui.tag));
        },
        afterTagRemoved: function(evt, ui) {
            addEvent('afterTagRemoved: ' + eventTags.tagit('tagLabel', ui.tag));
        },
        onTagClicked: function(evt, ui) {
            addEvent('onTagClicked: ' + eventTags.tagit('tagLabel', ui.tag));
        },
        onTagExists: function(evt, ui) {
            addEvent('onTagExists: ' + eventTags.tagit('tagLabel', ui.existingTag));
        }
    });


    $('#keywordsTags').tagit({
        availableTags: sampleTags,
        allowSpaces: true
    });
    $('#authorsTags').tagit({
        availableTags: sampleTags_2,
        allowSpaces: true
    });
    
});

function check_searching () {

    var doc_title = $("#doc_title").val();
    var types = [];
    var year_range = [];

    var keywords = "";
    var i = 0;
    $("#keywordsTags").find('span[class=tagit-label]').each(function () {
        keywords = keywords + $(this).text() + ",";
    });
    $("#keywords_input").val(keywords);

    var authors = "";
    $("#authorsTags").find('span[class=tagit-label]').each(function () {
        authors = authors + $(this).text() + ",";
    });
    $("#authors_input").val(authors);

    if ($("#type_conf").is(":checked")){
       types.push("conference");
    }
    if ($("#type_jour").is(":checked")){
        types.push("journal");
    }
    if ($("#type_book").is(":checked")){
        types.push("book");
    }
    if ($("#type_other").is(":checked")){
        types.push("other");
    }
    
    var year_from = $("#doc_year_from option:selected").text();
    year_range.push(year_from);

    var year_to = $("#doc_year_to option:selected").text();
    year_range.push(year_to);

    return true;


}