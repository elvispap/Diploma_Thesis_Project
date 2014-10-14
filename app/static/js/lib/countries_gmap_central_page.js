  
  google.load("visualization", "1", {packages:["geomap"]});
  google.setOnLoadCallback(drawMap);

  function drawMap() {

      $.ajax({
          url:"/access_db/",
          type: "GET",
          dataType: "json",
          data: {'action':"access_db_total_countries_central_page"},
          success:function(returned_data){

            var data = google.visualization.arrayToDataTable(returned_data);
            var options = {};
            options['dataMode'] = 'regions';
            options['height'] = '600';
            options['width'] = '1400';
            options['showZoomOut'] = true;
            
            var container = document.getElementById('total_counties_box');
            var geomap = new google.visualization.GeoMap(container);

            geomap.draw(data, options);
              
              
          },
          error: function(XMLHttpRequest, textStatus, errorThrown) { 
            console.log("Status: " + textStatus); alert("Error: " + errorThrown); 
          }       
        
      });
     
      
    
};

