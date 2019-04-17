function initialize(){
  $(".metadata-container").hide();
  console.log('Start')

  // grab tree coord info from tree, this will be used to intialize WebGl
  drawingData.nodeCoords = [0, 0, 0, 0, 0];
  drawingData.highTri = [];
  drawingData.numBranches = tree.edgeData.length
  drawingData.initZoom = tree.maxes.dim;
  drawingData.currentZoom = drawingData.initZoom;

  // Fill 'Tip color' drop down menu
  // fillDropDownMenu(tree.headers.general, "#tip-color-options");
  fillDropDownMenu(tree.headers.tip_cat, "#tip-color-options");
  fillDropDownMenu(tree.headers.tip_num, "#tip-color-options");

  // File 'Node color' drop down menu
  // fillDropDownMenu(tree.headers.general, "#branch-color-options");
  fillDropDownMenu(tree.headers.node_headers, "#branch-color-options");

  // TODO: create clade coloring drop box
  // fillDropDownMenu(tree.m_headers.all, '#clade-options');

  $("#show-metadata").prop('checked', true);

  // intializes webgl and creates callback events for users inputs
  initWebGl(tree.edgeData);
  initCallbacks();
  setPerspective();
  requestAnimationFrame(loop);
}