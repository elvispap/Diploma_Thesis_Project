var map2;
var resized;
$(document).ready(function() {

    google.maps.event.addDomListener(window, 'load', initialize);
   
    $("#hide_affiliations_col").click(function(){
        $("#map_col_2").animate({
            width: '100%', 
            height: 830, 
            marginLeft:0, 
            marginTop: 0
        }, resized);

        var currCenter = map2.getCenter();
         map2.setCenter(currCenter);
        
        $("#hide_affiliations_col").hide();
        $("#search_div").hide();
        $("#show_affiliations_col").fadeIn(1100);
       
    });
    $("#show_affiliations_col").click(function(){
        
        $("#map_col_2").animate({
            width:'75%'},1500);

        $("#show_affiliations_col").hide();
        $("#search_div").fadeIn(2000);
        $("#hide_affiliations_col").fadeIn(1100);
    });

    $(".affiliation").click(function(){
        var position = $(this).attr('id');
        var coords = position.split(",");
        map2.setZoom(14);
        map2.setCenter(new google.maps.LatLng(coords[0],coords[1]));
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

});

function initialize() {
    
    geocoder = new google.maps.Geocoder();
    var myLatlng1 = new google.maps.LatLng(39.304063,21.845854);
    var mapOptions = {
              center: myLatlng1,
              zoom: 3
    };
    map2 = new google.maps.Map(document.getElementById("map_col_2"),mapOptions);
    
    google.maps.event.addListenerOnce(map2, 'idle', function() {
        // $('.hide').hide();
        // $('.hide').css('height', '500px');
        $('#map_col_2').css({
           height:'830px',
           width:'75%'
        });
        console.log("still loaded");
    });

    resized = function() {
        // simple animation callback - let maps know we resized
        google.maps.event.trigger(map2, 'resize');
    };

    var data = localStorage.getItem("map_content");
    showMarkers( JSON.parse(data));

}

function showMarkers(affiliations){
    
    var position;
    var freq;
    var affiliation;
    var coll_authors;
    var markers = [];

    //console.log(affiliations.length);
    for (var i=0; i<affiliations.length; i++) {
        
        affiliation_name = affiliations[i]["affiliation_name"];
        affiliation_id = affiliations[i]["affiliation_id"];
        affiliation_location = affiliations[i]["affiliation_location"].split(",");
       
        var image = "../static/img/marker_2.png";
        var marker = new google.maps.Marker({
            position: new google.maps.LatLng(affiliation_location[0],affiliation_location[1]),
            map: map2,
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
    var markerCluster = new MarkerClusterer(map2, markers,mcOptions);
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

                var links = "";
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

                var marker_content = "<div id='marker_content'><label class='marker_tit'>"+affiliation_name+"</label><hr><div id='marker_co_names'><label class='marker_con'>Collaborative authors:</label><br><div class='main_content'>" + links_2 + "" + links + "</div></div><br><br><div id='marker_publications'><label class='marker_con'>Publications: </label><br><div class='main_content'>"+ links_3 +"</div></div></div>";
                var infowindow = new google.maps.InfoWindow({
                    content: marker_content
                });

                infowindow.open(marker.get('map'), marker);
            }     
        
        });
    });
}
