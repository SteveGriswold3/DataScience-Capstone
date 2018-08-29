// javascript
var width = 960,
    height = 350;

var y = d3.scale.linear()
    .range([height, 0]);

var chart = d3.select(".chart")
    .attr("width", width)
    .attr("height", height);
    
d3.json("/state_count.json", function(data) {

    var defaultColor = 'steelblue';
    var modeColor = '#4CA9F5'

    var maxY = d3.max(data, function(d) { return d.count; });
    y.domain([0, maxY]);

    var varColor = function(d, i) {
        if(d['count'] == maxY) {return modeColor; }
        else {return defaultColor}
    }
    var barWidth = width / data.length;
    var bar = chart.selectAll("g")
        .data(data)
        .enter()
        .append("g")
        .attr("transform", function(d, i) {
            return "translate(" + i * barWidth + ",0)"; });
    
    bar.append("rect")
        .attr("y", function(d) { return y(d.count); })
        .attr("height", function(d) { return height - y(d.count); })
        .attr("width", barWidth -1)
        .style("fill", varColor);
    
    bar.append("text")
        .attr("x", barWidth / 2)
        .attr("y", function(d) { return y(d.count) + 3; })
        .attr("dy", ".75em")
        .text(function(d) { return d.count; });
});
