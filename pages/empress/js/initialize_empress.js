function initialize(){
  $(".metadata-container").hide();
  console.log('Start')
  drawingData.nodeCoords = [0, 0, 0, 0, 0];
  drawingData.highTri = [];
  drawingData.numBranches = tree.edgeData.length
  drawingData.initZoom = tree.maxes.dim;
  drawingData.currentZoom = drawingData.initZoom;
  fillDropDownMenu(tree.m_headers.numeric, "#tip-color-options");
  fillDropDownMenu(tree.m_headers.cat, "#branch-color-options");
  // fillDropDownMenu(tree.m_headers.all, '#clade-options');

  $("#show-metadata").prop('checked', true);

  initWebGl(tree.edgeData);
  initCallbacks();
  setPerspective();
  requestAnimationFrame(loop);
}