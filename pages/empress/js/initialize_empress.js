function initialize(){
  let nodeCoords;

  $(".metadata-container").hide();
  console.log('Start')
  drawingData.nodeCoords = [0, 0, 0, 0, 0];
  drawingData.numBranches = window.edgeData.length
  drawingData.initZoom = window.max;
  drawingData.currentZoom = drawingData.initZoom;
  fillDropDownMenu(window.m_headers, "#highlight-options");
  fillDropDownMenu(window.m_headers, '#clade-options');
  fillDropDownMenu(window.m_headers, '#collapse-options');

  $("#show-metadata").prop('checked', true);

  initWebGl(window.edgeData);
  initCallbacks();
  setPerspective();
  requestAnimationFrame(loop);
}