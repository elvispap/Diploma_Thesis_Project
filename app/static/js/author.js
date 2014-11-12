$(document).ready(function() {

    var author_name = document.getElementById("authorName").innerHTML;
    
    $(".target").tipper({
        direction: "top",
        follow: true,
        
    });

    jQuery.expr[':'].Contains = function(a, i, m) {
        return jQuery(a).text().toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
    };
    $('#search_publication_cited_author').on('keyup', function() {

        var value = $(this).val();
        if (value) {
            $('#cited_publications li').hide();
            $('#cited_publications li:Contains('+value+')').show();
        } else {
            $('#cited_publications li').show();                  
        }
    });

    var canvas = document.getElementById('myCanvas'),context = canvas.getContext('2d');
    // resize the canvas to fill browser window dynamically
    window.addEventListener('resize', resizeCanvas, false);
    
    function resizeCanvas() {
            canvas.width = window.innerWidth - 50;
    }
    resizeCanvas();
        
    $(".citation_clicked").click(function(){
        $(this).parent().next(".cited_publications_div").slideToggle();
    });

    $("#co_authors_more").click(function(){
        $("#tab-content5").animate({height:'100%'},1200);
        $("#co_authors_more").hide();
        $("#co_authors_less").fadeIn(100);

    });

    $("#co_authors_less").click(function(){
        // $("#row2").css({"max-height":"300px"});
        $("#tab-content5").animate({height:'200px'},1200);
        $("#co_authors_less").hide();
        $("#co_authors_more").fadeIn(100);

    });

    $("#search_again").click(function(){
        $("#keywords_search_content").hide();   
        $("#keywords_more").show();
        $("#row2").fadeIn(1100);
        
    });

    $.ajax({
        url:"/access_db/",
        type: "GET",
        data: {'action':"access_db_publications_doc_types_author_2",'author':author_name},
        success:function(data){

            var conferences = data[0];
            var journals = data[1];
            var books = data[2];
            var others = data[3];

            var x_label_years = [];
            var conferences_freq = [];
            var journals_freq = [];
            var books_freq = [];
            var others_freq = [];
            
            for (var i = 0; i < conferences.length; i++) { 
                x_label_years.push(conferences[i][0]);

                conferences_freq.push(conferences[i][1]);
                journals_freq.push(journals[i][1]);
                books_freq.push(books[i][1]);
                others_freq.push(others[i][1]);
            }
      
            draw_graph_doc_types2(x_label_years,conferences_freq,journals_freq,books_freq,others_freq,"type_2_div","Production by publication type");
            
        }     
    });

    $.ajax({
            url:"/access_db/",
            type: "GET",
            data: {'action':"access_db_publications",'author':author_name,'source':'author'},
            success:function(data){
               
                var cit = 0;
                var years = []
                var freq = []
                var new_data = []

                for (var i = 0; i < data.length; i++) { 
                  
                    freq.push(data[i]['pub'][1]);
                    years.push(data[i]['pub'][0]);
                    cit = cit + data[i]["pub"][1];
                }
                console.log("TOTAL PUBS:",cit);
                var result = freq.concat();
    
                for (var i = 0; i < freq.length; i++){
                    result[i] = freq.slice(0, i + 1).reduce(function(p, i){ return p + i; });
                }
                 for(var i = 0; i < freq.length; i++){
                    new_data.push([years[i],result[i]]);
                }
                draw_graph_documents(new_data,author_name,"pubs_div","Cumulative publications published","Publications");
            }     
        
        
        });

        $.ajax({
            url:"/access_db/",
            type: "GET",
            data: {'action':"access_db_publications_citations",'author':author_name,'source':'author'},
            success:function(data){
                // console.log(data);
                var new_data = [];
                var years = [];
                var citations = [];
                new_data = data[0];
                var cit = 0;
                for (var i = 0; i < data.length; i++) { 
                    years.push(data[i]["pub"][0]);
                    citations.push(data[i]["pub"][1]);
                    cit = cit + data[i]["pub"][1];
                }
                //console.log("TOTAL CITATIONS:",cit);
                var result = citations.concat();
        
                for (var i = 0; i < citations.length; i++){
                    result[i] = citations.slice(0, i + 1).reduce(function(p, i){ return p + i; });
                }
                var new_data = [];
                for(var i = 0; i < citations.length; i++){
                    new_data.push(result[i]);
                }
               
                //draw_citations_cum(new_data);
                draw_graph_citations(new_data,years,author_name,"cita_div","Citations");
            }     
        });

        $("#type_cum").click(function(){
        
            $.ajax({
                url:"/access_db/",
                type: "GET",
                data: {'action':"access_db_publications_citations",'author':author_name,'source':'author'},
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
                    draw_graph_citations(new_data,years,author_name,"cita_div","Citations");
                }     
            });
        });

        $("#type_ann").click(function(){
 
            $.ajax({
                url:"/access_db/",
                type: "GET",
                data: {'action':"access_db_publications_citations",'author':author_name,'source':'author'},
                success:function(data){

                    var new_data = [];
                    var years = [];
                    var citations = [];
            
                    for (var i = 0; i < data.length; i++) { 
                        years.push(data[i]["pub"][0]);
                        new_data.push([data[i]['pub'][0],data[i]['pub'][1]]);
                    }
                    draw_graph_citations(new_data,years,author_name,"cita_div","Citations");
                }     
            });
        });
        $.ajax({
            url:"/access_db/",
            type: "GET",
            data: {'action':"access_db_publications_doc_types_author_1",'author':author_name},
            success:function(data){
                draw_graph_doc_types1(data,"type_1_div","Publications type");
            }     
        });


    $("#main_dataBTN").click(function(){
        $(this).css({"font-weight": "bold"});
        $(this).css({"color": "black"});

        $("#docsBTN").css({"color":"#A5A5A5"});
        $("#collBTN").css({"color":"#A5A5A5"});
        $("#cited_byBTN").css({"color":"#A5A5A5"});    
        $("#keywsBTN").css({"color":"#A5A5A5"});    

     
        $("#documents_div").hide();
        $("#keywords_div").hide();
        $("#cited_by_div").hide();
        $("#collborators_div").hide();
        $("#main_data_div").fadeIn(1500);
      
    });

    $("#keywsBTN").click(function(){

         $.ajax({
            url:"/access_db/",
            type: "GET",
            data: {'action':"access_db_author_profile_keywords",'author':author_name},
            success:function(data){
             //authors/([^/]+)/keywords/([^/]+)$
                console.log(data.length);
                var all_keywords = "";
                for (var i = 0; i < data.length; i++) {
                    var keyw_value  = data[i]['keyw'];
                    var keyw_size  = data[i]['size'];
                    var keyw = "<li><a href='/authors/"+author_name.trim().replace(" ","_")+"/keywords/"+keyw_value.replace(" ","_")+"' class='size-"+keyw_size+" keyw_tag'>"+keyw_value+"</a></li>";
                    all_keywords = all_keywords + keyw;
                    
                }
          
                $("#keywords ul").append(all_keywords);

                if(!$('#myCanvas').tagcanvas({
                      textColour: '#31ACF3',
                      outlineMethod: "size",
                      outlineIncrease:2,
                      wheelZoom : true,
                      depth: 1.5,
                      zoomMin: 0.8,
                      maxSpeed: 0.003,
                      weight : true,
                      dragThreshold : 1
                },'keywords')) {
                  // something went wrong, hide the canvas container
                  $('#row2').hide();
                }
                $("#keywsBTN").css({"font-weight":"bold"});
                $("#keywsBTN").css({"color": "black"});
                
                $("#docsBTN").css({"color":"#A5A5A5"});
                $("#main_dataBTN").css({"color":"#A5A5A5"});
                $("#collBTN").css({"color":"#A5A5A5"});
                $("#cited_byBTN").css({"color":"#A5A5A5"});  
                
                 $("#documents_div").hide();
                $("#main_data_div").hide();
                $("#cited_by_div").hide();
                $("#collborators_div").hide();
                $("#keywords_div").fadeIn(1500);
            }     
        });
    });

    $(".cited_byBTN").click(function(){

        $.ajax({
            url:"/access_db/",
            type: "GET",
            data: {'action':"access_db_publications_cited_by",'author':author_name},
            success:function(data){
                console.log(data.length);
                var all_links = "";
                for (var i = 0; i < data.length; i++) {
                    var title  = data[i]['pub'][0];
                    var url  = data[i]['pub'][1];
                    var link = "<li><a class='citation' href="+url+">"+title+"</a></li>";
                    all_links = all_links + link;
                    
                }
          
                $("#cited_publications ul").append(all_links);
                $("#cited_byBTN").css({"font-weight": "bold"});
                $("#cited_byBTN").css({"color": "black"});
                $("#docsBTN").css({"color":"#A5A5A5"});
                $("#main_dataBTN").css({"color":"#A5A5A5"});
                $("#collBTN").css({"color":"#A5A5A5"});
                 $("#keywsBTN").css({"color":"#A5A5A5"}); 

                $("#keywords_div").hide(); 
                $("#documents_div").hide();
                $("#main_data_div").hide();
                $("#collborators_div").hide();
                $("#cited_by_div").fadeIn(1500);
            }     
        });

    });

    $(".collBTN").click(function(){
        $("#collBTN").css({"font-weight": "bold"});
        $("#collBTN").css({"color": "black"});
        $("#docsBTN").css({"color":"#A5A5A5"});
        $("#main_dataBTN").css({"color":"#A5A5A5"});
        $("#keywsBTN").css({"color":"#A5A5A5"});
        $("#cited_byBTN").css({"color":"#A5A5A5"});
             
        $("#documents_div").hide();
        $("#main_data_div").hide();
        $("#keywords_div").hide();
        $("#cited_by_div").hide();
        $("#collborators_div").fadeIn(1500);
     
       
    });

    $(".docsBTN").click(function(){

        $("#docsBTN").css({"color": "black"});
        $("#docsBTN").css({"font-weight": "bold"});
        $("#main_dataBTN").css({"color":"#A5A5A5"});
         $("#cited_byBTN").css({"color":"#A5A5A5"}); 
        $("#collBTN").css({"color":"#A5A5A5"});
        $("#keywsBTN").css({"color":"#A5A5A5"}); 

        $("#tab-content2_tab-content3").hide();
        $("#collborators_div").hide();
        $("#main_data_div").hide();
        $("#keywords_div").hide();
        $("#cited_by_div").hide();
        $("#documents_div").fadeIn(1500);
    });

    $("#tab-content5").each(function(){
        var $this = $(this);
        if ($this.get(0).scrollHeight > $this.height()) {
            console.log("yess");
            $("#co_authors_more").show();
        }
        else
            console.log("noo");
    });
  
});

function draw_graph_documents(data,author_name,div,title,source) {
        
        $('#'+div+'').highcharts({
        chart: {
            type: 'column'
        },
        title: {
           text: title,
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
                text: source,
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
            enabled:false
        },
        legend: {
            enabled: false
        },
        tooltip: {
            pointFormat: '<b>{point.y:.0f} '+source+'</b>'
        },
        series: [{
            name: source,
            data: data,
            pointWidth: 10,
            dataLabels: {
                enabled: true,
                rotation: -90,
                color: '#FFFFFF',
                align: 'right',
                x: 4,
                y: 10,
                style: {
                    fontSize: '13px',
                    fontFamily: 'Verdana, sans-serif',
                    textShadow: '0 0 3px black'
                }
            }
        }]
    });
       
   
        
}

function draw_graph_citations (data,x_label_years,author_name,div,source) {

    $('#'+div+'').highcharts({
           title: {
                text: "",
               // x: -20 //center
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
                    text: source,
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
                name: 'Number of '+source+'',
                data: data
            }]
        });
}

function draw_graph_doc_types1 (data,div,title) {

       $('#'+div+'').highcharts({
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false
            },
            credits: {
                enabled: false
            },
            title: {
                text: title
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            exporting: { 
                enabled: false 
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                        style: {
                            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        },
                        connectorColor: 'silver'
                    }
                }
            },
            series: [{
                type: 'pie',
                name: 'Amount',
                pointWidth: 10,
                data: data
            }]
    });
}

function draw_graph_doc_types2(x_label_years,conferences_freq,journals_freq,books_freq,others_freq,div,title){

    $('#'+div+'').highcharts({
        chart: {
            type: 'column',
            spacingBottom: 35
        },
        credits: {
            enabled: false
        },
        title: {
            text: title

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
            name: 'Journals',
            data: journals_freq,
            pointWidth: 10
        }, {
            name: 'conferences',
            data: conferences_freq,
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







