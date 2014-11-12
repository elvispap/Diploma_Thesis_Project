var map;
var ext_data;
var resized;
$(document).ready(function() {


    google.maps.event.addDomListener(window, 'load', initialize);

    $("#total_countriesBTN").click(function(){
        
        $('#container_affiliations_index').hide();
        $('#affiliations_div').hide();
        $(".svg_container").hide();
        $("#total_counties_box").slideToggle();
    }); 

    $("#main_areasBTN").click(function(){
        
        $('#container_affiliations_index').hide();
        $("#affiliationsBtn_hide").hide();
        $("#total_counties_box").hide();
        $(".svg_container").slideToggle();
        
    });    


   $.ajax({
        url:"/access_db/",
        type: "GET",
        data: {'action':"access_db_publications_citations",'author':"index",'source':'index'},
        success:function(data){

            var new_data = [];
            var citations = [];
            var years = [];
            for (var i = 0; i < data.length; i++) { 
                citations.push(data[i]['pub'][1]);
                years.push(data[i]['pub'][0]);
            }
            var result = citations.concat();

            for (var i = 0; i < citations.length; i++){
                result[i] = citations.slice(0, i + 1).reduce(function(p, i){ return p + i; });
            }

            for(var i = 0; i < citations.length; i++){
                new_data.push([years[i],result[i]]);
            }
            //localStorage.setItem("citations_cumulative_data", JSON.stringify(new_data));  // store all the data 
            draw_citations_cum(new_data);
           
        }     
            
    });

    $("#type_cum").click(function(){
       
        
           
            $.ajax({
                url:"/access_db/",
                type: "GET",
                data: {'action':"access_db_publications_citations",'author':"index",'source':'index'},
                success:function(data){

                    var new_data = [];
                    var citations = [];
                    var years = [];
                    for (var i = 0; i < data.length; i++) { 
                        citations.push(data[i]['pub'][1]);
                        years.push(data[i]['pub'][0]);
                    }
                    var result = citations.concat();
        
                    for (var i = 0; i < citations.length; i++){
                        result[i] = citations.slice(0, i + 1).reduce(function(p, i){ return p + i; });
                    }

                    for(var i = 0; i < citations.length; i++){
                        new_data.push([years[i],result[i]]);
                    }
                   
                    draw_citations_cum(new_data);
                   
                }     
                
            });
        
        
    });

    $("#type_ann").click(function(){
        
        var freq = [];
        var x_label_years = []

        
            $.ajax({
                url:"/access_db/",
                type: "GET",
                data: {'action':"access_db_publications_citations",'author':"index",'source':'index'},
                success:function(data){

                    var new_data = [];
                    var citations = [];
                    var years = [];
                    for (var i = 0; i < data.length; i++) { 
                        x_label_years.push(data[i]['pub'][0]);
                        freq.push(data[i]['pub'][1]);
                    }
                    draw_citations_ann(x_label_years,freq);
                }     
                
            });
    });

    $("#hide_affiliations_col").click(function(){

        $("#map_col").animate({
            width: '100%', 
            height: 630, 
            marginLeft:0, 
            marginTop: 0
        }, resized);

        var currCenter = map.getCenter();
        //google.maps.event.trigger(map, 'resize');
        map.setCenter(currCenter);
        
        $("#hide_affiliations_col").hide();
        $("#search_div").hide();
        $("#show_affiliations_col").fadeIn(1100);
       
    });
    $("#show_affiliations_col").click(function(){
        
        $("#map_col").animate({
            width:'75%'},1500);
        // $("#map_col").animate({
        //     left:'200px'},1200);

        $("#show_affiliations_col").hide();
        $("#search_div").fadeIn(2000);
        $("#hide_affiliations_col").fadeIn(1100);
    });

    $(".affiliation").click(function(){
        var position = $(this).attr('id');
        var coords = position.split(",");
        console.log(position);
        console.log(coords[0]+","+coords[1]);
        map.setZoom(14);

        map.setCenter(new google.maps.LatLng(coords[0],coords[1]));

    });
    $("#affiliationsBtn_show").click(function(){
       
        $(".svg_container").hide();
        $("#total_counties_box").hide();
        $('#container_affiliations_index').slideToggle();
        google.maps.event.trigger(map, 'resize');
        map.setZoom(3);
        var myLatlng = new google.maps.LatLng(39.304063,21.845854);
        map.setCenter(myLatlng);
        
    });

    jQuery.expr[':'].Contains = function(a, i, m) {
        return jQuery(a).text().toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
    };
    $('#search_affiliation').on('keyup', function() {

        var value = $(this).val();
        if (value) {
            $('#affiliations_ul li').hide();
            $('#affiliations_ul li:Contains('+value+')').show();
        } else {
            $('#affiliations_ul li').show();                  
        }
    });

    jQuery.expr[':'].Contains = function(a, i, m) {
        return jQuery(a).text().toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
    };
    $('#search_publication_keyword').on('keyup', function() {
        $("#search_message").fadeOut(200);
        $("#search_for_keyword_div").show();
        var value = $(this).val();
        if (value) {
            $('#keywords_ul li').hide();
            $('#keywords_ul li:Contains('+value+')').show();

        } else {
            $('#keywords_ul li').show();
            $("#search_for_keyword_div").hide();                  
        }

    });

    $(".keyword").click(function(){
        $("#search_publication_keyword").val($(this).text());
        $("#search_for_keyword_div").hide();
    });

    $("#search_by_keyword_icon").click(function(){
        if($("#search_publication_keyword").val() == "") {
            $("#search_message").empty().append("Please write a keyword...");
            $("#search_message").fadeIn(300);
        }else{
            if($("#search_publication_keyword").val() == "") 
                console.log("dont send");
            else
                $("#search_by_keyword_form").submit();
        }
    });

    var conferences = [];
    var conferences_freq = [];
    var journals = [];
    var journals_freq = [];
    var books = [];
    var books_freq = [];
    var others = [];
    var others_freq = [];

    var freq = [];
    var x_label_freq = [];
    var affiliations = [];

    $.ajax({
            url:"/access_db/",
            type: "GET",
            data: {'action':"access_db_publications_doc_types_index",'author':"index",'source':'index'},
            success:function(data){
                conferences = data[0];
                journals = data[1];
                books = data[2];
                others = data[3];
                var x_label_years = [];
                for (var i = 0; i < conferences.length; i++) { 
                    x_label_years.push(conferences[i]["conference"][0]);
                    conferences_freq.push(conferences[i]["conference"][1]);

                }
                for (var i = 0; i < journals.length; i++) { 
                   
                    journals_freq.push(journals[i]["journal"][1]);
                    
                }
                for (var i = 0; i < books.length; i++) { 
                    
                    books_freq.push(books[i]["book"][1]);
                    
                }
                for (var i = 0; i < conferences.length; i++) { 
                    
                    others_freq.push(others[i]["other"][1]);
                    
                }
               
                draw_doc_types(x_label_years,conferences_freq,journals_freq,books_freq,others_freq);

               
            }     
            
    });
});

function draw_citations_cum(freq) {
        
       $('#container_citations').highcharts({
        chart: {
            type: 'column'
        },
        title: {
            text: ''
        },
        credits:{
            enabled:false
        },
        xAxis: {
            type: 'category',
            labels: {
                rotation: -45,
                style: {
                    fontSize: '10px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Citations',
                style: {
                    color: 'black',
                    font: 'normal 14px Verdana, sans-serif'

                 }
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            }
        },
        exporting:{
            enabled: false
        },
        legend: {
            enabled: false
        },
        tooltip: {
            pointFormat: '<b>{point.y:.0f} citations</b>'
        },
        series: [{
            name: 'Citations',
            data: freq,
            pointWidth: 10,
            dataLabels: {
                //enabled: true,
                // rotation: -90,
                // color: '#FFFFFF',
                // align: 'right'
                // x: 4,
                // y: 10,
                // style: {
                //     fontSize: '13px',
                //     fontFamily: 'Verdana, sans-serif',
                //     textShadow: '0 0 3px black'
                // }
            }
        }]
    });
        
}
function draw_citations_ann(x_label_years,freq) {
        
        $('#container_citations').highcharts({
            chart: {
                type: 'column'
            },
            title: {
                text: '',
                x: -20 //center
            },
            credits: {
                enabled: false
            },
            xAxis: {
                categories: x_label_years,
                labels: {
                    rotation: -45,
                    style: {
                        fontSize: '10px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Citations',
                    style: {
                        color: 'black',
                        font: 'normal 14px Verdana, sans-serif'

                     }
                },
                stackLabels: {
                    enabled: true,
                    style: {
                        fontWeight: 'bold',
                        color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                    }
                }
            },
            exporting: { 
                enabled: false 
            },
            tooltip: {
                // valueSuffix: '°C'
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: [{
                showInLegend: false,
                name: 'Citations',
                data: freq,
                pointWidth: 10
            }]
        });
   
        
}
function draw_doc_types(x_label_years,conferences_freq,journals_freq,books_freq,others_freq){
    $('#container_doc_types').highcharts({
        chart: {
            type: 'column',
            spacingBottom: 35
        },
        credits: {
            enabled: false
        },
        title: {
            text: ''

        },
        xAxis: {
            type: 'category',
            categories: x_label_years,
           
            labels: {
                rotation: -45,
                style: {
                    fontSize: '10px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Publications',
                style: {
                    color: 'black',
                    font: 'normal 14px Verdana, sans-serif'

                 }
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            }
        },
        exporting: { 
            enabled: false 
        },
        legend: {
            align: 'right',
            x: -0,
            verticalAlign: 'bottom',
            y: 30,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
            // borderColor: '#CCC',
            // borderWidth: 1,
            shadow: false
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.x + '</b><br/>' +
                    this.series.name + ': ' + this.y + '<br/>' +
                    'Total: ' + this.point.stackTotal;
            }
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                // dataLabels: {
                //     enabled: true,
                //     color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                //     style: {
                //         textShadow: '0 0 3px black, 0 0 3px black'
                //     }
                // }
            }
        },
        series: [{
            name: 'Conferences',
            data: conferences_freq,
            pointWidth: 10
        }, {
            name: 'Journals',
            data: journals_freq,
            pointWidth: 10
        }, {
            name: 'Books',
            data: books_freq,
            pointWidth: 10
        }, {
            name: 'Other',
            data: others_freq,
            pointWidth: 10
        }]
    });
}

function initialize() {

    geocoder = new google.maps.Geocoder();
    var myLatlng1 = new google.maps.LatLng(39.304063,21.845854);
    var mapOptions = {
              center: myLatlng1,
              zoom: 3
    };
    map = new google.maps.Map(document.getElementById("map_col"),mapOptions);
    
    google.maps.event.addListenerOnce(map, 'idle', function() {
        // $('.hide').hide();
        // $('.hide').css('height', '500px');
        console.log("still here index");
        $('#map_col').css({
           height:'630px',
           width:'75%'
        });
        // $("#map_col").animate({
        //     width:'100%'},1500);
    });

    resized = function() {
        // simple animation callback - let maps know we resized
        google.maps.event.trigger(map, 'resize');
    };


    $.ajax({
        url:"/access_db/",
        type: "GET",
        dataType: "json",
        data: {'action':"access_db_affiliations"},
        success:function(data){

            
            localStorage.setItem("map_content", JSON.stringify(data));  // store all the markers' content 
            showMarkers(data);
        }     
        
    });

   
    
    
    
    
    
}

function showMarkers(affiliations){
    
    var position;
    var freq;
    var affiliation;
    var coll_authors;
    var markers = [];

    console.log(affiliations.length);

    for (var i=0; i<affiliations.length; i++) {
        
        affiliation_name = affiliations[i]["affiliation_name"];
        affiliation_id = affiliations[i]["affiliation_id"];
        affiliation_location = affiliations[i]["affiliation_location"].split(",");
       
        
        var image = "../static/img/marker_2.png";
        var marker = new google.maps.Marker({
            position: new google.maps.LatLng(affiliation_location[0],affiliation_location[1]),
            map: map,
            id: affiliation_id,
            clickable: true,
            animation: google.maps.Animation.DROP,
            title:affiliation,
            icon:image
        });
        
        setListener(marker);
        markers.push(marker);

    }

    var mcOptions = {gridSize: 50, maxZoom: 15};
    var markerCluster = new MarkerClusterer(map, markers,mcOptions);
}


function setListener(marker){
    
    google.maps.event.addListener(marker, 'click', function() {

        $.ajax({
            url:"/access_db/",
            type: "GET",
            dataType: "json",
            data: {'action':"access_db_marker_content","marker_id":marker.id},
            success:function(affiliation){
                
                var affiliation_name = affiliation[0]["aff_name"];
                var ext_coll_authors = affiliation[0]["out_co_authors"];
                var freq = affiliation[0]["len_all_co_authors"];
                var coll_authors = affiliation[0]["dep_collaborated_authors"];   // a list of all authors
                var publications = affiliation[0]["publications"];   // a list of all publications

                var links = '';
                var c = 0;
                for( key in coll_authors){
                    c++;
                    var author = coll_authors[key];
                    var author_url = "/authors/"+ author.toLowerCase().replace(/ /g,"_")+"";
                    var logo = author.toLowerCase().replace(/ /g,"_");
                    
                    
                    links = links + "<div class='dep_author'> \
                                            <div class='marker_author_image'>  \
                                                <img src='../static/img/photo_profile/"+logo+".jpg' height='25' width='25'> \
                                            </div> \
                                            <div class='marker_author_name'> \
                                                <a class='text_4' href="+author_url+">" + author + "</a> \
                                            </div> \
                                         </div>";
                }

                var links_2 = "";
               for( key in ext_coll_authors){
                   
                    author = ext_coll_authors[key]["name"]
                    profile_url = ext_coll_authors[key]["profile_url"]
                    links_2 = links_2 + '<a class="text_3 marker_co_author" href="'+profile_url+'">'+author+'</a>';
                        
                }
                var links_3 = "";
                
                for( key in publications){
                   
                    title = publications[key]["title"];
                    url = publications[key]["url"];
                    links_3 = links_3 + '<a class="text_3 marker_publication" href="'+url+'"> - '+title+'</a><br>';
                   
                }
               
                var marker_content = "<div id='marker_content'><label class='marker_tit'>"+affiliation_name+"</label><hr> \
                                        <div id='marker_co_names'> \
                                            <label class='marker_con'>Collaborative authors:</label><br> \
                                            <div class='main_content'>" + links_2 + "" + links + "</div> \
                                        </div></br></br> \
                                        <div id='marker_publications'> \
                                            <label class='marker_con'>Publications: </label/><br> \
                                            <div class='main_content'>"+ links_3 +"</div> \
                                        </div> \
                                    </div>";

               
                var infowindow = new google.maps.InfoWindow({
                    content: marker_content
                });

                infowindow.open(marker.get('map'), marker);
            }     
        
        });
    });

}


