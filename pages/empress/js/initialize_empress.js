function initialize(){
  let nodeCoords;

  $(".metadata-container").hide();
  field.table_headers = {'headers': Object.keys(window.treeData['G000830275'])}
  console.log('Start')
  drawingData.nodeCoords = [0, 0, 0, 0, 0];
  //   edgeData = data.data;
  //   let max = data.max
    drawingData.numBranches = window.edgeData.length
    drawingData.initZoom = 1000;
    drawingData.currentZoom = drawingData.initZoom;
  //   console.log("recived data")
  // }).done(function() {
  //   $.getJSON(urls.trianglesURL, {}, function(data) {
      // drawingData.triangles = [];//extractInfo(data, field.triangleFields);
      // fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
  //   }).done(function() {
  //     requestAnimationFrame(loop);
  //   });
    fillDropDownMenu(field.table_headers.headers, "#highlight-options");
    fillDropDownMenu(field.table_headers.headers, '#clade-options');
    fillDropDownMenu(field.table_headers.headers, '#collapse-options');

    $("#show-metadata").prop('checked', true);

    initWebGl(window.edgeData);
    initCallbacks();
    setPerspective();
    requestAnimationFrame(loop);
  // });
}