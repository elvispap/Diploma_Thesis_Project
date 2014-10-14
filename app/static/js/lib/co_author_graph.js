var margin = {top: 20, right: 120, bottom: 20, left: 120},
    width = 1920 - margin.right - margin.left,
    height = 800 - margin.top - margin.bottom;

var svg = d3.select("#collborators_div").append("svg")
   
    .attr("class","svg_co_author_graph")
    .attr("width", width + margin.right + margin.left)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
   
var force = d3.layout.force()
    .gravity(.020)
    .distance(350)
    .charge(-10)
    .size([width, height]);



function loadData(json) {
  
  var edges = [];
    json.Links.forEach(function(e) { 
      var sourceNode = json.Nodes.filter(function(n) { return n.Id === e.Source; })[0],
      targetNode = json.Nodes.filter(function(n) { return n.Id === e.Target; })[0];
        
      edges.push({source: sourceNode, target: targetNode, value: e.Value});
    });
    
  force
      .nodes(json.Nodes)
      .links(edges)
      .start();

  var link = svg.selectAll(".link")
      .data(edges)
    .enter().append("line")
      .attr("class", "link");

  var node = svg.selectAll(".node")
      .data(json.Nodes)
      .enter().append("g")
      .attr("class", "node")
      .call(force.drag)
      .on("mouseover", function(d) 
      {
       
        d3.select(d.Name).style("visibility","visible")
      
      })
     .on("mouseout", function(d)
     {
        d3.select(d.Name).style("visibility","hidden")
     })

  node.append("circle")
      .attr("class", "node")
      .attr("r", function(d){return d.Weight;});

  node.append("svg:a")
      .attr("xlink:href", function(d){return d.Url;})
      .append("text")
      .attr("dx", 12)
      .attr("dy", ".35em")

      .text(function(d) { return d.Name})

  
  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
  });


}


var author_name = document.getElementById("authorName").innerHTML;
$.ajax({
    url:"/access_db/",
    type: "GET",
    data: {'action':"access_db_author_profile_co_authors",'author_name':author_name},
    success:function(data){
       
        loadData(data);

    },error: function(XMLHttpRequest, textStatus, errorThrown) { 
        alert("Error: " + errorThrown); 
    }  

});  

