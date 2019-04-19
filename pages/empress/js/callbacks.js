"use strict";

/**
 * tells javasript what function to call for mouse/keyboard events
 */
function initCallbacks(){
  const SHFT_KEY = 16;
  const DELAY = 500;
  window.onTreeSurface = false;
  window.timer = setTimeout(hover, 100, 0, 0);
  $(".tree-surface").on("mousedown", mouseHandler);
  $(document).on("mouseup", mouseHandler);
  $(document).on("mousemove", mouseHandler);
  $(".tree-surface")[0].onwheel = mouseHandler;
  $(".tree-surface").hover(function() {window.onTreeSurface = true;},
      function(){window.onTreeSurface=false;})
  $(window).on("resize", resizeCanvas);

  $(".tree-surface")[0].ondblclick = mouseHandler;

  $(document).keydown(function(e) {
    shftPress = (e.which === SHFT_KEY) ? true : false;
  });
  $(document).keyup(function() {
    if(shftPress) {
      shftPress = false;
    //   let square = $(".square");
    //   let offset = square.offset();
    //   drawingData.lastMouseX = offset.left, drawingData.lastMouseY = offset.top;
    //   let width = square.width(), height = square.height();
    //   let topCorner = toTreeCoords(drawingData.lastMouseX, drawingData.lastMouseY);
    //   let bottomCorner = toTreeCoords(drawingData.lastMouseX + width, drawingData.lastMouseY + height);
    //   let edgeMetadata;
    //   $.getJSON(urls.selectTreeURL, {x1: topCorner[0], y1: topCorner[1],
    //             x2: bottomCorner[0], y2: bottomCorner[1]}, function(data) {
    //     edgeMetadata = data;
    //   }).done(function() {
    //     if(edgeMetadata.length === 0) {
    //       $(".selected-tree-menu").css({top: drawingData.lastMouseY, left: drawingData.lastMouseX, visibility: "hidden"});
    //       return;
    //     }
    //     drawingData.selectTree = extractInfo(edgeMetadata, field.edgeFields);
    //     updateGridData(edgeMetadata);
    //     fillBufferData(shaderProgram.selectBuffer, drawingData.selectTree);
    //     $(".selected-tree-menu").css({top: drawingData.lastMouseY, left: drawingData.lastMouseX, visibility: "visible"});
    //     requestAnimationFrame(loop);
    //   });
    }
  });
}


function changeTaxSys() {
  let origChecked = !$("#curation").is(":checked");
  retrieveTaxonNodes("t");
  retrieveTaxonNodes("n");
  if ($("#collapse-cb").is(":checked") && !origChecked) {
    autoCollapseTree();
  }
  if (origChecked) {
    $("#collapse-cb").attr("checked", false);
    $("#collapse-cb").attr("disabled", true);
    $("#internal-nodes").attr("checked", false);
    $("#internal-nodes").attr('disabled',true);
    autoCollapseTree();
    retrieveTaxonNodes("n");
  } else {
    $("#collapse-cb").attr("disabled", false);
    $("#internal-nodes").attr('disabled',false);
  }
}

function getTaxPrefix() {
  let taxSys = $("input[name='sys']:checked").val();
  let taxType = $("#curation").is(":checked") ? "c_" : "o_";
  // let taxType = $("input[name='type']:checked").val();
  let taxPrefix = taxSys + taxType;
  return taxPrefix;
}


/**
 * Canvas hover event.
 * @function hover
 * @param {number} x - x-coordinate
 * @param {number} y - y-coordinate
 */
function hover(x, y) {
  if ($("body").css("cursor") !== "none") {
    nodeHover(x, y);
    triangleHover(x, y);
  }
}


/**
 * Hover on node.
 * @function nodeHover
 * @param {number} x - x-coordinate
 * @param {number} y - y-coordinate
 */
function nodeHover(x, y) {
  let id;
  let clsXTC, clsYTC, clsID;
  let close = 1000;
  let tmp;
  let xDist, yDist, treeX, treeY, nScreenX, nScreenY, treeSpace, screenSpace;
  let canvas = $(".tree-surface")[0];
  for (id in tree.tree) {
    treeX = tree.tree[id].x;
    treeY = tree.tree[id].y;

    // calculate the screen coordinate of the label
    treeSpace = vec4.fromValues(treeX, treeY, 0, 1);
    screenSpace = vec4.create();
    vec4.transformMat4(screenSpace, treeSpace, shaderProgram.mvpMat);
    screenSpace[0] /= screenSpace[3];
    screenSpace[1] /= screenSpace[3];
    nScreenX = (screenSpace[0] * 0.5 + 0.5) * canvas.offsetWidth;
    nScreenY = (screenSpace[1] * -0.5 + 0.5) * canvas.offsetHeight;
    xDist = x - nScreenX;
    yDist = y - nScreenY;

    tmp = xDist * xDist + yDist * yDist;

    if (Math.abs(tmp) < close) {
      close = Math.abs(tmp);
      clsXTC = treeX;
      clsYTC = treeY;
      clsID = id;
    }
  }

  // generate hover box
  let box = document.getElementById("hover-box");
  box.classList.add("hidden");

  if (close <= 50 && (clsID === "N1" || tree.metadata[clsID]["branch_is_visible"])) {
    drawingData.hoveredNode = [clsXTC, clsYTC, 0, 1, 0];

    nodeHoverBox(clsID);

    // calculate the screen coordinate of the label
    let treeSpace = vec4.fromValues(clsXTC, clsYTC, 0, 1);
    let screenSpace = vec4.create();
    vec4.transformMat4(screenSpace, treeSpace, shaderProgram.mvpMat);
    screenSpace[0] /= screenSpace[3];
    screenSpace[1] /= screenSpace[3];
    let pixelX = (screenSpace[0] * 0.5 + 0.5) * canvas.offsetWidth;
    let pixelY = (screenSpace[1] * -0.5 + 0.5) * canvas.offsetHeight;

    // show hover box
    box.style.left = Math.floor(pixelX + 23) + "px";
    box.style.top = Math.floor(pixelY - 43) + "px";
    box.classList.remove("hidden");
  }

  fillBufferData(shaderProgram.hoverNodeBuffer, drawingData.hoveredNode);
  requestAnimationFrame(loop);
}


/**
 * Hover on clade.
 * @function triangleHover
 * @param {number} x - x-coordinate
 * @param {number} y - y-coordinate
 */
function triangleHover(x, y) {
  let treeCoords = toTreeCoords(x, y);
  let triRoot = tree.triangleAt(treeCoords[0], treeCoords[1]);

  if (triRoot != null) {
    let box = document.getElementById("hover-box");
    box.classList.add("hidden");

    cladeHoverBox(triRoot.id);

    // show hover box
    box.style.left = (x + 23) + "px";
    box.style.top = (y - 43) + "px";
    box.classList.remove("hidden");

    drawingData.highTri = triRoot.tri;
    fillBufferData(shaderProgram.highTriBuffer, drawingData.highTri);
  } else {
    drawingData.highTri = [];
  }
  requestAnimationFrame(loop);
}


/**
 * Refresh hover box for node.
 * @function nodeHoverBox
 * @param {number} clsID - node ID
 */
function nodeHoverBox(clsID) {
  let taxPrefix = getTaxPrefix();
  let table = document.getElementById("hover-table");
  table.innerHTML = "";

  // Id row
  let row = table.insertRow(-1);
  let cell = row.insertCell(-1);
  cell.innerHTML = "ID";
  cell = row.insertCell(-1);
  cell.innerHTML = clsID;

  // links row
  if (clsID[0] === "G") {
    row = table.insertRow(-1);
    cell = row.insertCell(-1);
    cell.innerHTML = "Links";
    cell = row.insertCell(-1);
    cell.innerHTML = "<a href='"
      + "https://www.ncbi.nlm.nih.gov/assembly/"
      + tree.metadata[clsID]["assembly_accession"]
      + "' target='_blank'>NCBI</a>";
    const img_id = tree.metadata[clsID]["img_id"];
    if (img_id !== null) {
      cell.innerHTML += " | <a href='"
        + "https://img.jgi.doe.gov/cgi-bin/m/main.cgi?section=TaxonDetail"
        + "&page=taxonDetail&taxon_oid=" + img_id
        + "' target='_blank'>IMG</a>";
    }
    const gtdb_id = tree.metadata[clsID]["gtdb_id"]
    if (gtdb_id !== null) {
      cell.innerHTML += " | <a title='" + gtdb_id + "' href='"
        + "http://gtdb.ecogenomic.org/genomes?gid=" + gtdb_id.slice(3)
        + "' target='_blank'>GTDB</a>";
    }
  }

  // taxon count row
  if (clsID[0] === "N") {
    row = table.insertRow(-1);
    cell = row.insertCell(-1);
    cell.innerHTML = "Taxa";
    cell = row.insertCell(-1);
    cell.innerHTML = tree.tree[clsID]["leafcount"];
  }

  // rank rows
  if (clsID !== "N1") {
    ranks.forEach(function(rank) {
      const name = tree.metadata[clsID][taxPrefix + rank];
      if (name) {
        row = table.insertRow(-1);
        cell = row.insertCell(-1);
        cell.innerHTML = rank;
        cell = row.insertCell(-1);
        cell.innerHTML = name;
      }
    });
  }

  // download row
  if (clsID[0] === "G") {
    row = table.insertRow(-1);
    cell = row.insertCell(-1);
    cell.colSpan = 2;
    const btn = document.createElement("button");
    btn.innerHTML = "Download";
    btn.onclick = function () {
      window.open(getDownloadURL(clsID), "_blank");
    };
    cell.appendChild(btn);
  }

  // export row
  else {
    createExportBtn(table, clsID);
  }
}


/**
 * Refresh hover box for collapsed clade.
 * @function cladeHoverBox
 * @param {number} clsID - node ID
 */
function cladeHoverBox(clsID) {
  let table = document.getElementById("hover-table");
  table.innerHTML = "";

  let sel = document.getElementById("collapse-level");
  let taxLevel = sel.options[sel.selectedIndex].value;
  let taxPrefix = getTaxPrefix();

  // name row
  let row = table.insertRow(-1);
  let cell = row.insertCell(-1);
  cell.innerHTML = taxLevel;
  cell = row.insertCell(-1);
  cell.innerHTML = tree.metadata[clsID][taxPrefix + taxLevel];

  // taxon count row
  row = table.insertRow(-1);
  cell = row.insertCell(-1);
  cell.innerHTML = "Taxa";
  cell = row.insertCell(-1);
  cell.innerHTML = tree.tree[clsID]["leafcount"];

  // export button
  createExportBtn(table, clsID);
}


/**
 * Create an "Export" button in a hover box.
 * @function createExportBtn
 * @param {Object} table - table in the hover box
 * @param {number} clsID - current node Id
 */
function createExportBtn(table, clsID) {
  let row = table.insertRow(-1);
  let cell = row.insertCell(-1);
  cell.colSpan = 2;
  const btn = document.createElement("button");
  btn.innerHTML = "Export";
  btn.onclick = function () {
    let modal = document.getElementById("export-modal");
    modal.dataset.clsID = clsID;
    modal.firstElementChild.firstElementChild.firstElementChild.innerHTML
      = clsID + " (" + tree.tree[clsID]["leafcount"] + " genomes)";
    modal.classList.remove("hidden");
  };
  cell.appendChild(btn);
}


function autoCollapseTree() {
  let selectElm = $("#collapse-level");
  let taxSys = $("input[name='sys']:checked").val();
  let taxPrefix = taxSys + "d_";
  if ($("#collapse-cb").is(":checked")) {
    selectElm.attr("disabled", false);
    let taxLevel = selectElm.val();
    let edgeData = tree.collapse(taxLevel, taxPrefix);
    drawingData.numBranches = edgeData.length;
    drawingData.triangles = tree.triData;
    fillBufferData(shaderProgram.treeVertBuffer, edgeData);
    fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
  } else {
    selectElm.attr("disabled", true);
    let edgeData = tree.uncollapse();
    drawingData.numBranches = edgeData.length;
    drawingData.triangles = tree.triData;
    fillBufferData(shaderProgram.treeVertBuffer, edgeData);
    fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
  }

  clearLabels("tip-label-container");
  clearLabels("node-label-container");
  retrieveTaxonNodes('t');
  retrieveTaxonNodes('n');
  requestAnimationFrame(loop);
}

function selectedTreeCollapse() {
  $(".selected-tree-menu").css({visibility: "hidden"})
  $.getJSON(urls.collapseSTreeURL, {}, function(data) {
    let edgeData = extractInfo(data, field.edgeFields);
    drawingData.numBranches = edgeData.length
    fillBufferData(shaderProgram.treeVertBuffer, edgeData);
    drawingData.selectTree = [];
    fillBufferData(shaderProgram.selectBuffer, drawingData.selectTree);
    $.getJSON(urls.trianglesURL, {}, function(data) {
      drawingData.triangles = extractInfo(data, field.triangleFields);
      fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
    }).done(function() {
      requestAnimationFrame(loop);
    });
  });
}


function clearSelectedTreeCollapse(event) {
  let treeCoords = toTreeCoords(event.clientX, event.clientY);
  $.getJSON(urls.uncollapseSTreeURL, {x1: treeCoords[0], y1: treeCoords[1]}, function(data) {
    let edgeData = extractInfo(data, field.edgeFields);
    drawingData.numBranches = edgeData.length
    fillBufferData(shaderProgram.treeVertBuffer, edgeData);
    drawingData.selectTree = [];
    fillBufferData(shaderProgram.selectBuffer, drawingData.selectTree);
    $.getJSON(urls.trianglesURL, {}, function(data) {
      drawingData.triangles = extractInfo(data, field.triangleFields);
      fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
    }).done(function() {
      requestAnimationFrame(loop);
    });
  });
}


/**
 * Resize the drawing canvas to fix the screen.
 * @param {Object} resize - event used to dynamically resize the html document.
 */
function resizeCanvas(event) {
  setCanvasSize(gl.canvas);
  setPerspective();
  requestAnimationFrame(loop);
}


/**
 * Display a color key in the legend box.
 * @param {string} name - key name
 * @param {Object} info - key information
 * @param {Object} container - container DOM
 * @param {boolean} gradient - gradient or discrete
 */
function addColorKey(name, info, container, gradient) {
  if (name) {
    let div = document.createElement("div");
    div.classList.add("legend-title");
    div.innerHTML = name;
    container.appendChild(div);
  }
  if (gradient) {
    addContinuousKey(info, container);
  } else {
    addCategoricalKey(info, container);
  }
}


/**
 * Format a number that is to be displayed in a label.
 * @param {number} num - number to be formatted
 * @returns {string} formatted number
 */
function formatNumLabel(num) {
  return num.toPrecision(4).replace(/\.?0+$/, "");
}


/**
 * Display a continuous color key.
 * @param {Object} info - key information
 * @param {Object} container - container DOM
 */
function addContinuousKey(info, container) {
  // create key container
  let div = document.createElement("div");
  div.classList.add("gradient-bar");

  // min label
  let component = document.createElement("label");
  component.classList.add("gradient-label");
  component.innerHTML = formatNumLabel(info.min[0]);
  div.appendChild(component);

  // color gradient
  component = document.createElement("div");
  component.classList.add("gradient-color");
  component.setAttribute("style", "background: linear-gradient(to right, " +
    info.min[1] + " 0%, " + info.max[1] + " 100%);");
  div.appendChild(component);

  // max label
  component = document.createElement("label");
  component.classList.add("gradient-label");
  component.innerHTML = formatNumLabel(info.max[0]);
  div.appendChild(component);

  container.appendChild(div);
}


/**
 * Display a categorical color key.
 * @param {Object} info - key information
 * @param {Object} container - container DOM
 */
function addCategoricalKey(info, container) {
  let key;
  let category = container.innerText;
  let i = 0;
  for (key in info) {
    // create key container
    let div = document.createElement("div");
    div.classList.add("gradient-bar");

    // color gradient
    let component = document.createElement("div");
    component.classList.add("category-color");
    component.setAttribute("style", "background: " + info[key] + ";");
    component.addEventListener("click", function(color, cat, val) { return function () {
        test(color, cat, val);
      };
    }(info[key], category, key), false)
    div.appendChild(component);

    // label
    component = document.createElement("label");
    component.classList.add("gradient-label");
    component.innerHTML = key;
    component.title = key;
    div.appendChild(component);

    container.appendChild(div);
  }
}

/*
 *
*/
function test(color, cat, val) {
  console.log(color);
  console.log(cat);
  console.log(val);
}

/**
 * Event called when user presses the select-data button.
 * @function userHighlightSelect
 * This method is responsible for coordinating the highlight tip feature.
 */
function userHighlightSelect() {
  const RANKS = ["kingdom", "phylum", "class", "order", "family", "genus", "species"  ];
  const RANK_PREFIX = getTaxPrefix();
  let edgeData;
  let selectElm = $("#collapse-level");
  let tipKey = document.getElementById("tip-color-key");
  let nodeKey = document.getElementById("node-color-key");
  let presetKey = document.getElementById("preset-color-key");
  let result;

  // reset color key
  tipKey.innerHTML = "";
  tipKey.classList.add("hidden");
  nodeKey.innerHTML = "";
  nodeKey.classList.add("hidden");
  presetKey.innerHTML = "";
  presetKey.classList.add("hidden");

  // reset tree back to default color
  // TODO: this method can be optimized to make this action unnecessary
  if (!$("#branch-color").is(":checked") || !$("#tip-color").is(":checked")) {
    $("#tip-color-options").attr("disabled", true);
    $("#branch-color-options").attr("disabled", true);
    edgeData = tree.colorBranches("default")["edgeData"];
  }

  // color tree using preset
  if ($("#preset-color").is(":checked")) {
    result = tree.colorBranches("(preset)")
    addColorKey("preset", result["keyInfo"], presetKey, false)
    presetKey.classList.remove("hidden");
    edgeData = result["edgeData"];
  }
  // color branches
  if ($("#branch-color").is(":checked")) {
    let cat = $("#branch-color-options").val();
    cat = (RANKS.includes(cat)) ? RANK_PREFIX + cat : cat;
    $("#branch-color-options").attr("disabled", false);
    result = tree.colorBranches(cat, "N");
    addColorKey(cat, result["keyInfo"], nodeKey, result["gradient"]);
    nodeKey.classList.remove("hidden");
    edgeData = result["edgeData"];
  }

  // color tips
  if ($("#tip-color").is(":checked")) {
    let cat = $("#tip-color-options").val();
    cat = (RANKS.includes(cat)) ? RANK_PREFIX + cat : cat;
    $("#tip-color-options").attr("disabled", false);
    result = tree.colorBranches(cat, "G");
    tipKey.classList.remove("hidden");
    addColorKey(cat, result["keyInfo"], tipKey, result["gradient"]);
    edgeData = result["edgeData"];
  }

  // update color any collapsed triangles
  if ($("#collapse-cb").is(":checked")) {
    let taxLevel = selectElm.val();
    let taxSys = $("input[name='sys']:checked").val();
    let taxPrefix = taxSys + "d_";
    tree.collapse(taxLevel, taxPrefix);
    drawingData.numBranches = edgeData.length;
    drawingData.triangles = tree.triData;
    fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
  }

  // draw tree
  fillBufferData(shaderProgram.treeVertBuffer, edgeData);
  requestAnimationFrame(loop);
}

/*
 * Reads custom user metadata and adds it to tree.metadata. This will also color the tree using the file.
 * param {Object} file - the metadata file
*/
function uploadFile(file) {
  let reader = new FileReader();

  // set file name
  let fname = file.name.substring(0, file.name.lastIndexOf("."));

  // extract metadata and color tree
  reader.onload = function(e) {
    parseMetadataString(e.target.result, fname);

    // TODO: need to color tree using first color
  }
  reader.readAsText(file);
}

/*
 * Parses metadata file text and stores it in tree.metadata
 * @param {string} metadata string
 * @param {string} fname name of file, will be used as header if metadata does not have one.
 * @ returns {boolean} true if success, false if error occured.
*/
function parseMetadataString(metadata, fname) {

  let result = {};
  // error occured if tab was not used
  if (metadata.indexOf("\t") === -1) {
    toastMsg("File Error: file must be tab delimited.");
    result["success"] = false;
    return result;
  }

  // convert metadata string into array
  const LINE_BREAK = "line_break";
  metadata = metadata.replace(/\n/g,"\t" + LINE_BREAK + "\t").split("\t");
  metadata.pop();

  // check to see if metadata has header
  let hasHeader = (metadata[0] in tree.metadata) ? false : true;
  metadata[0] = (hasHeader) ?  "Node_id" : metadata[0];

  // calculate number of columns
  let colNum = metadata.findIndex(function(element) {
    return element === LINE_BREAK;
  });

  // error occured if hasHeader is false and colNum > 2
  if (!hasHeader && colNum > 2) {
    toastMsg("File Error: too many columns, please use column headers");
    result["success"] = false;
    return result;
  }

  // grab headers from metadata or set headers to default value
  let headers;
  if (hasHeader) {
    headers = Array.from(Array(colNum), (x, i) => metadata[i]);
  }
  else {
    headers = ["Node_id", fname];
  }

  // initialize variables for loop
  let startIndex = (hasHeader) ? headers.length + 1 : 0;
  let numRows = metadata.length / (headers.length + 1);
  numRows = (hasHeader) ? numRows - 1 : numRows;
  let numCols = headers.length;
  let curIndex = startIndex, i, j, curID;
  let warning = false;
  let maxes = {}, number, col;
  let prefix;
  // extract metadata and store it in tree.metadata
  for(i = 0; i <  numRows; i++) {

    // TODO: make warning if ID is not in tree
    curID = metadata[curIndex];
    if (!(curID in tree.metadata)) {
      toastMsg("Warning: " + curID + " is not a valid ID.");

      // set warning flag to true so only one warning pops up
      // Note: flag is not being used right now
      warning = true;
      curIndex = curIndex + numCols + 1;
      continue;
    }
    curIndex += 1;
    for (j = 1; j < numCols; j++) {
      if (metadata[curIndex] === "") {
        tree.metadata[curID][headers[j]] = null;
      }
      else {
        if (!isNaN(parseFloat(metadata[curIndex]))) {
          number = parseFloat(metadata[curIndex]);
          col = headers[j];
          tree.metadata[curID][col] = number;
          prefix = (curID[0] === "G") ? "g_" : "n_";


          // add header to approperiate drop down menu
          if (curID[0] === "G" && !tree.headers.tip_num.includes(col)) {
            tree.headers.tip_num.push(col);
          }
          else if (curID[0] === "N" && !tree.headers.node_headers.includes(col)) {
            tree.headers.node_headers.push(col);
          }

          // caclulate new min/max for column
          if (!(prefix + col in maxes)) {
            maxes[prefix + col] = {min: number, max: number}
          }
          else if (maxes[prefix + col]["min"] > number){
            maxes[prefix + col]["min"] = number;
          }
          else if (maxes[prefix + col]["max"] < number) {
            maxes[prefix + col]["max"] = number;
          }

        }
        else {
          tree.metadata[curID][headers[j]] = metadata[curIndex];

          // add header to approperiate drop down menu
          if (curID[0] === "G" && !tree.headers.tip_cat.includes(headers[j])) {
            tree.headers.tip_cat.push(headers[j]);
          }
          else if (curID[0] === "N" && !tree.headers.node_headers.includes(headers[j])) {
            tree.headers.node_headers.push(headers[j]);
          }
        }
      }
      curIndex += 1;
    }

    // error occured if number of columns is not uniformm throughout file
    if(metadata[curIndex] !== LINE_BREAK) {
      toastMsg("File Error: columns have different sizes.");
      result["success"] = false;
      return result;
    }
    curIndex += 1;
  }

  // add new headers to drop down menus
  let tips = document.getElementById("tip-color-options");
  tips.innerHTML = "";
  fillDropDownMenu(tree.headers.tip_cat, "#tip-color-options");
  fillDropDownMenu(tree.headers.tip_num, "#tip-color-options");
  let nodes = document.getElementById("branch-color-options");
  nodes.innerHTML = "";
  fillDropDownMenu(tree.headers.node_headers, "#branch-color-options");

  // add maxes to tree.maxes
  let max;
  for (max in maxes) {
    tree.maxes[max] = [maxes[max]["min"], maxes[max]["max"]];
  }

  // return the newly added columns
  result["success"] = true;
  result["headers"] = headers;
  return result;
}

function userCladeColor(){
  const attribute = $('#clade-options').val();
  const taxLevel = $("#tax-level").val();
  const cm = $("#color-options-tax").val();
  $.getJSON(urls.newCladeColor, {attribute: attribute, tax_level: taxLevel, cm: cm}, function(data){
      loadColorClades(data);
  })
}

function retrieveTaxonNodes(triggerBy) {
  let taxLevel;
  let node;
  let selectElm, numElm;
  let taxPrefix = getTaxPrefix();
  if(triggerBy === 't' && $("#tips").is(":checked")) {
    selectElm = $("#tips-find-level");
    numElm = $("#tips-number");
    selectElm.attr("disabled", false);
    numElm.attr("disabled", false);
    taxLevel = selectElm.val();
    if(tipLabels.length < 1) {
      tipLabels = tree.getTaxonLabels(taxLevel, "true", taxPrefix, random);
    }
  }
  else if(!$("#tips").is(":checked")) {
    $("#tips-find-level").attr('disabled',true);
    $("#tips-number").attr('disabled',true);
    tipLabels = [];
  }

  if(triggerBy === 'n' && $("#internal-nodes").is(":checked")) {
    selectElm = $("#nodes-find-level");
    numElm = $("#internal-nodes-number")
    selectElm.attr("disabled", false);
    numElm.attr("disabled", false);
    taxLevel = selectElm.val();
    nodeLabels = tree.getTaxonLabels(taxLevel, "false", taxPrefix, highToLow);
  }
  else if(!$("#internal-nodes").is(":checked")) {
    $("#nodes-find-level").attr("disabled", true);
    $("#internal-nodes-number").attr("disabled", true);
    nodeLabels = [];
  }
  if(parseInt($("#tips-number").val()) > 100) {
    $("#tips-number").val("100");
  }
  if(parseInt($("#internal-nodes-number").val()) > 100) {
    $("#internal-nodes-number").val("100");
  }
  drawingData.numTipLabels = parseInt($("#tips-number").val());
  drawingData.numNodeLabels = parseInt($("#internal-nodes-number").val());
  requestAnimationFrame(loop);
}

function clearLabels(container) {
   let divContainerElement = document.getElementById(container);
    while(divContainerElement.firstChild) {
      divContainerElement.removeChild(divContainerElement.firstChild);
    }
}

/**
 * Changes the metadata shown in SlickGrid to match the highlighted feature that
 * was selected.
 *
 * @param {Object} The button that corresponds to the highlighted feature.
 */
function selectTable(obj) {
  const item = attrItem[obj.parentElement.id];
  let l = '', u = '', e = '';
  if(item.operator === " > " ) {
    l = item.compVal;
  } else if(item.operator === " < ") {
    u = item.compVal;
  } else {
    e = item.compVal;
  }
  $.getJSON(urls.tableChangeURL, {attribute: item.attr, lower: l, equal: e,
            upper: u}, function(data){
    updateGridData(data);
  });
}

/**
 *
 */
function extractLabels(labs, labId) {
  let tempLabels = {};
  for(let i in labs) {
    let label = labs[i];
    let l = {
      x : label["x"],
      y : label["y"],
      label : label[labId]
    };
    tempLabels[i] = l;
  }
  let numLabels = Object.keys(tempLabels).length;
  labels = new Array(numLabels);
  for(let i = 0; i < numLabels; ++i) {
    labels[i] = [tempLabels[i].x, tempLabels[i].y, tempLabels[i].label];
  }
  requestAnimationFrame(loop);
}

function fillBufferData(buffer, data) {
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.DYNAMIC_DRAW);
}

function newTree() {
  const attr = $("#highlight-options").val();
  const l = $("#lower-bound").val();
  const u = $("#upper-bound").val();
  const e = $("#category").val();
  $.getJSON(urls.subTreeURL, {attribute: attr, lower: l, equal: e,
            upper: u}, function(data){
    loadTree(data);
  }).done(function() {
    $.getJSON(urls.cladeURL, {}, function(data) {
      loadColorClades(data);
    });
  });
}

function getOldTree(event) {
  $.getJSON(urls.oldTreeURL, {}, function(data){
    if(data.length == 0) {
      return;
    }
    loadTree(data);
  }).done(function() {
    $.getJSON(urls.cladeURL, {}, function(data) {
      loadColorClades(data);
    });
  });
}


/**
 * Generate a URL toward NCBI FTP genome download.
 * @function getDownloadURL
 * @param {string} id - genome Id
 * @param {string} target - specific file (e.g., "genomic.fna.gz")
 */
function getDownloadURL(id, target) {
  const acc = tree.metadata[id]["assembly_accession"];
  const asm = tree.metadata[id]["asm_name"].replace(/[\s#]/g, "_");
  let url = "ftp://ftp.ncbi.nlm.nih.gov/genomes/all/" + acc.substr(0, 3) + "/"
    + acc.substr(4, 3) + "/" + acc.substr(7, 3) + "/" + acc.substr(10, 3) + "/"
    + acc + "_" + asm;
  if (target !== undefined) {
    url += "/" + acc + "_" + asm + "_" + target;
    if (!target.endsWith(".gz")) {
      url += ".gz";
    }
  }
  return url;
}


/**
 * Generate a text file for download.
 * @function downloadText
 * @param {string} text - file content
 * @param {string} fname - file name
 */
function downloadText(text, fname) {
  var a = document.createElement("a");
  a.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(text));
  a.setAttribute("download", fname);
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}


/**
 * Download genome Id list as a text file.
 * @function downloadGenomeIds
 */
function downloadGenomeIds(clsID) {
  let genomeIds = tree.getGenomeIDs(clsID);
  genomeIds.sort();
  downloadText(genomeIds.join("\r\n") + "\r\n", clsID + ".ids.txt");
}


/**
 * Download genome download links as a text file.
 * @function downloadLinks
 */
function downloadLinks(clsID) {
  let sel = document.getElementById("downfile-options");
  let target = sel.options[sel.selectedIndex].value;
  let genomeIds = tree.getGenomeIDs(clsID);
  genomeIds.sort();
  let links = "";
  genomeIds.forEach(function(id) {
    links += getDownloadURL(id, target) + "\r\n";
  });
  downloadText(links, clsID + ".links.txt");
}


/**
 * Download subtree as a Newick file.
 * @function downloadSubtree
 */
function downloadSubtree(clsID) {
    downloadText(tree.toNewick(clsID) + ";", clsID + ".nwk");
}


/**
 * Perform quick search.
 * @function quickSearch
 */
function quickSearch() {
  let bar = document.getElementById("quick-search");
  let keyword = bar.value;
  bar.value = "";

  // obtain and sort candidate Ids
  let taxPrefix = getTaxPrefix();
  let metaKeys = Object.keys(tree.metadata);
  let ids = metaKeys.filter(function(x) {
    return x.startsWith("G");
  });
  ids.sort(sort2ndNum);
  if (taxPrefix.endsWith("c_")) {
    let nIds = metaKeys.filter(function(x) {
      return x.startsWith("N") && x !== "N1";
    });
    nIds.sort(sort2ndNum);
    ids = nIds.concat(ids);
  }

  // search for keyword
  let target = searchKeyword(keyword, taxPrefix, ids);

  // not found
  if (!target) {
    toastMsg("Keyword \"" + keyword + "\" is not found.");
    return;
  }

  // found but invisible
  if (!tree.metadata[target]["branch_is_visible"]) {
    toastMsg("Found " + target + " but it is currently invisible.");
    return;
  }

  // show hover box
  const treeX = tree.tree[target].x;
  const treeY = tree.tree[target].y;
  drawingData.hoveredNode = [treeX, treeY, 0, 1, 0];

  // calculate the screen coordinate of the label
  let canvas = document.querySelector(".tree-surface");
  let treeSpace = vec4.fromValues(treeX, treeY, 0, 1);
  let screenSpace = vec4.create();
  vec4.transformMat4(screenSpace, treeSpace, shaderProgram.mvpMat);
  screenSpace[0] /= screenSpace[3];
  screenSpace[1] /= screenSpace[3];
  let pixelX = (screenSpace[0] * 0.5 + 0.5) * canvas.offsetWidth;
  let pixelY = (screenSpace[1] * -0.5 + 0.5) * canvas.offsetHeight;

  // show hover box
  let box = document.getElementById("hover-box");
  box.classList.add("hidden");
  nodeHoverBox(target);
  box.style.left = Math.floor(pixelX + 23) + "px";
  box.style.top = Math.floor(pixelY - 43) + "px";
  box.classList.remove("hidden");
}


/**
 * Sort genome/node IDs by numeric part from 2nd character
 * @function sort2ndNum
 * @param {string} a - left side
 * @param {string} b - right side
 */
function sort2ndNum(a, b) {
  return parseInt(a.slice(1)) - parseInt(b.slice(1));
}


/**
 * Perform quick search.
 * @function searchKeyword
 * @param {string} keyword - search keyword
 * @param {string} prefix - taxonomic prefix
 * @param {string} ids - genome or node ID list
 */
function searchKeyword(keyword, taxPrefix, ids) {
  for (const rank of ranks) {
    for (const id of ids) {
      const name = tree.metadata[id][taxPrefix + rank];
      if (name && name.includes(keyword)) {
        return id;
      }
    }
  }
  return null;
}


/**
 * Display a message in toast.
 * @function toastMsg
 * @param {string} msg - message to display
 * @param {number} duration - milliseconds to keep toast visible
 */
function toastMsg(msg, duration) {
  duration = duration || 2000;
  var toast = document.getElementById("toast");
  toast.innerHTML = msg;
  toast.classList.remove("hidden");
  setTimeout(function(){
    toast.classList.add("hidden");
  }, duration);
}
