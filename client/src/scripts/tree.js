import colorFromStr from '../scripts/colorize';

const tooltip = d3.select("body")
      .append("div")
      .attr("class", "tooltip")
      .style("position", "absolute")
      .style("z-index", "999")
      .style("visibility", "hidden");

function updateHover(node, remove, callback) {
  callback(node, remove);

  if (node.children) {
    node.children.forEach(child => updateHover(child, remove, callback));
  }
}


function update(root, tree, svg, diagonal, sourceMap, hoverCallback) {
  let i = 0;

  // Compute the new tree layout.
  const nodes = tree.nodes(root).reverse(),
    links = tree.links(nodes);

  // Normalize for fixed-depth.
  nodes.forEach(function(d) { d.y = d.depth * 57.5; });
  nodes.forEach(function(d) { d.x *= 2; });

  // Declare the nodes…
  var node = svg.selectAll("g.node")
	  .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Enter the nodes.
  var nodeEnter = node.enter().append("g")
	  .attr("class", "node")
	  .attr("transform", function(d) {
		  return "translate(" + d.x + "," + d.y + ")"; });

  nodeEnter.append("circle")
	  .attr("r", 20)
	  .style("fill", function (d) {
	    if (d.sourceId) {
	      return colorFromStr(d.sourceId);
      }

	    return '#FFF';
    })
    .on('mouseover', function(d) {
      updateHover(d, false, hoverCallback);

      if (d.hoverValue) {
        tooltip.style("visibility", "visible")
          .html(d.hoverValue.join('<br />'));

        return;
      }

      const sourceList = sourceMap[d.sourceId];
      if (sourceList) {
        tooltip.style("visibility", "visible")
          .html(sourceMap[d.sourceId].join('<br />'));
      }
    })
    .on("mousemove", function() {
      return tooltip.style("top", (d3.event.pageY + 15) + "px").style("left", (d3.event.pageX + 15) + "px");
    })
    .on("mouseout", function(d) {
      updateHover(d, true, hoverCallback);

      return tooltip.style("visibility", "hidden");
    });

  nodeEnter.append("text")
	  .attr("y", 0)
	  .attr("dy", ".30em")
	  .attr("text-anchor", "middle")
    .attr("pointer-events", "none")
    .style("font-family", "Roboto")
    .style("font-size", function(d) {
      return d.children ? '20px' : '14px';
    })
	  .text(function(d) {
	    return d.value;
	  })
	  .style("fill-opacity", 1);

  // Declare the links…
  var link = svg.selectAll("path.link")
	  .data(links, function(d) { return d.target.id; });

  // Enter the links.
  link.enter().insert("path", "g")
	  .attr("class", "link")
	  .attr("d", diagonal);
}

export default function drawTree(parentComponent, sourceMap, root, hoverCallback) {
  // Clear any old trees
  const componentId = `#${parentComponent}`;
  d3.select(componentId).select("svg").remove();

  // If there is no tree, return after removing the previous one
  if (!root) {
    return;
  }

  let margin = {top: 30, right: 5, bottom: 5, left: 5},
  width = 625 - margin.right - margin.left,
  height = 375 - margin.top - margin.bottom;

  let tree = d3.layout.tree()
    .size([height, width]);

  let diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.x, d.y]; });

  let svg = d3.select(componentId).append("svg")
    .attr("width", width + margin.right + margin.left)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  update(root, tree, svg, diagonal, sourceMap, hoverCallback);
}
