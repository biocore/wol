function initialize(){
  $(".metadata-container").hide();
  console.log('Start')
  drawingData.nodeCoords = [0, 0, 0, 0, 0];
  drawingData.numBranches = tree.edgeData.length
  drawingData.initZoom = tree.max;
  drawingData.currentZoom = drawingData.initZoom;
  fillDropDownMenu(tree.m_headers, "#highlight-options");
  fillDropDownMenu(tree.m_headers, '#clade-options');

  $("#show-metadata").prop('checked', true);

  initWebGl(tree.edgeData);
  initCallbacks();
  setPerspective();
  requestAnimationFrame(loop);
}