"use strict";

function loop() {
  gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

  // calculate where the virtual camera is
  let hCamPos = vec4.fromValues(camera.pos[0], camera.pos[1], camera.pos[2], 1);
  let hLookDir = vec4.fromValues(camera.lookDir[0], camera.lookDir[1], camera.lookDir[2], 1);
  vec4.transformMat4(hCamPos, hCamPos, shaderProgram.xyTransMat);
  vec4.transformMat4(hCamPos, hCamPos, shaderProgram.zTransMat);
  vec4.transformMat4(hLookDir, hLookDir, shaderProgram.xyTransMat);


  // create virtual camera
  let camPos = vec3.create();
  let lookDir = vec3.create();
  vec3.copy(camPos, hCamPos);
  vec3.copy(lookDir, hLookDir);
  shaderProgram.viewMat  = mat4.create();
  mat4.lookAt(shaderProgram.viewMat, camPos, lookDir, camera.upDir);

  // calculate the model view matrix
  shaderProgram.mvpMat = mat4.create();
  mat4.multiply(shaderProgram.mvpMat, shaderProgram.projMat, shaderProgram.viewMat);
  mat4.multiply(shaderProgram.mvpMat, shaderProgram.mvpMat, shaderProgram.worldMat);

  gl.clear(gl.COLOR_BUFFER_BIT);

  // pass the model view matrix to webgl
  gl.uniformMatrix4fv(shaderProgram.mvpUniform, false, shaderProgram.mvpMat);

  // draw any highlighted clades
  bindBuffer(shaderProgram.cladeVertBuffer);
  gl.drawArrays(gl.TRIANGLES, 0, drawingData.coloredClades.length / 5);


  // draw any nodes
  gl.uniform1i(shaderProgram.isSingle, 1);
  bindBuffer(shaderProgram.treeVertBuffer);
  gl.drawArrays(gl.POINTS, 0, drawingData.numBranches / 5 );
  // draw hovered node
  bindBuffer(shaderProgram.hoverNodeBuffer);
  gl.drawArrays(gl.POINTS, 0, drawingData.hoveredNode.length / 5 );

  // draw the tree
  gl.uniform1i(shaderProgram.isSingle, 0);
  bindBuffer(shaderProgram.treeVertBuffer);
  gl.drawArrays(gl.LINES, 0, drawingData.numBranches / 5 );

  bindBuffer(shaderProgram.selectBuffer);
  gl.drawArrays(gl.LINES, 0, drawingData.selectTree.length / 5);

  bindBuffer(shaderProgram.triangleBuffer);
  gl.drawArrays(gl.TRIANGLES, 0, drawingData.triangles.length / 5);

  drawLabels();
}

/*
 * sends a buffer to webgl to draw
 */
function bindBuffer(buffer) {
  // defines constants for a vertex. A vertex is the form [x, y, r, g, b]
  const VERTEX_SIZE = 5;
  const COORD_SIZE = 2;
  const COORD_OFFSET = 0;
  const COLOR_SIZE = 3;
  const COLOR_OFFEST = 2;

  // tell webgl which buffer to store the vertex data in
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);

  // tell webgl where the x,y coords are in the array
  gl.vertexAttribPointer(
    shaderProgram.positionAttribLocation,
    COORD_SIZE,
    gl.FLOAT,
    gl.FALSE,
    VERTEX_SIZE * Float32Array.BYTES_PER_ELEMENT,
    COORD_OFFSET
  );

  // tel webgl where the r,g,b values are in the array
  gl.vertexAttribPointer(
    shaderProgram.colorAttribLocation,
    COLOR_SIZE,
    gl.FLOAT,
    gl.FALSE,
    VERTEX_SIZE * Float32Array.BYTES_PER_ELEMENT,
    COLOR_OFFEST * Float32Array.BYTES_PER_ELEMENT
  );
}

function drawLabels() {
  const NEGATE = -1;

  let canvas = $(".tree-surface")[0];

  const X = 0;
  const Y = 1;
  const VALUE = 2;
  const ID = 3;
  const NODE = 4;

  // // find the top left corner of the viewing window in tree space
  let boundingBoxDim = camera.pos[2] + shaderProgram.zTransMat[14];
  let topLeft = vec4.fromValues(NEGATE * boundingBoxDim, boundingBoxDim, 0, 1);
  vec4.transformMat4(topLeft, topLeft, shaderProgram.xyTransMat);

  // find the bottom right corner of the viewing window in tree space
  let bottom = NEGATE * camera["bottomSlope"] * boundingBoxDim;
  let bottomRight = vec4.fromValues(boundingBoxDim, bottom, 0, 1);
  vec4.transformMat4(bottomRight, bottomRight, shaderProgram.xyTransMat);

  // find where the range of the viewing window along the the x/y axis
  let minX = topLeft[X], maxX = bottomRight[X];
  let minY = bottomRight[Y], maxY = topLeft[Y];

  // remove old labels
  let divContainerElement = document.getElementById("tip-label-container");

   // predefine variables need in for loop to speed up loop
  let childLabels = divContainerElement.getElementsByTagName("div");
  let i, k;
  let left, top;
  let pixelX = 0, pixelY = 0;
  let div, textNode;
  let treeSpace = vec4.create();
  let screenSpace = vec4.create();
  let treeX, treeY, numLabels;
  if(childLabels.length > 0) {
    for(i = 0; i < childLabels.length; i++) {
      // left = childLabels[i].style.left;
      // top = childLabels[i].style.top;
      left = childLabels[i].x;
      top = childLabels[i].y;
      if(minX <= left && left <= maxX &&
        minY <= top && top <= maxY) {
        console.log("change")
        k = childLabels[i].id;
        console.log(k)
        // calculate the screen coordinate of the label
        treeSpace = vec4.fromValues(tipLabels[k][X], tipLabels[k][Y], 0, 1);
        screenSpace = vec4.create();
        vec4.transformMat4(screenSpace, treeSpace, shaderProgram.mvpMat);
        screenSpace[0] /= screenSpace[3];
        screenSpace[1] /= screenSpace[3];
        pixelX = (screenSpace[0] * 0.5 + 0.5) * canvas.offsetWidth;
        pixelY = (screenSpace[1] * -0.5 + 0.5)* canvas.offsetHeight;

        // update position
        childLabels[i].style.left = Math.floor(pixelX) + "px";
        childLabels[i].style.top = Math.floor(pixelY) + "px";
      } else {
        console.log("delete")
        divContainerElement.removeChild(childLabels[i]);
      }
    }
  }

   // draw top 10 tip labels within the viewing window
  numLabels = tipLabels.length;
  let count = divContainerElement.getElementsByTagName("div").length;
  for(i = 0; i < numLabels; ++i) {
    if(count === 10) {
        break;
    }
    k = Math.floor(Math.random() * numLabels);
    // grad x,y coordinate of node in tree space and check to see if its in the viewing window
    treeX = tipLabels[k][X];
    treeY = tipLabels[k][Y];
    if(minX <= treeX && treeX <= maxX &&
        minY <= treeY && treeY <= maxY) {
      // calculate the screen coordinate of the label
      treeSpace = vec4.fromValues(tipLabels[k][X], tipLabels[k][Y], 0, 1);
      screenSpace = vec4.create();
      vec4.transformMat4(screenSpace, treeSpace, shaderProgram.mvpMat);
      screenSpace[0] /= screenSpace[3];
      screenSpace[1] /= screenSpace[3];
      pixelX = (screenSpace[0] * 0.5 + 0.5) * canvas.offsetWidth;
      pixelY = (screenSpace[1] * -0.5 + 0.5)* canvas.offsetHeight;

      // make the div
      div = document.createElement("div");

      // assign it a CSS class
      div.className = "floating-div";

      // make a text node for its content
      textNode = document.createTextNode(tipLabels[k][VALUE]);
      div.appendChild(textNode);

      // add it to the divcontainer
      divContainerElement.appendChild(div);
      div.style.left = Math.floor(pixelX) + "px";
      div.style.top = Math.floor(pixelY) + "px";
      div.id = k;
      div.x = treeX;
      div.y = treeY;

      // stop once 10 labels have been drawn to screen
      count++;
    }
  }

  // remove old labels
  divContainerElement = document.getElementById("node-label-container");
  while(divContainerElement.firstChild) {
    divContainerElement.removeChild(divContainerElement.firstChild);
  }

  // draw top 10 node labels within the viewing window
  count = 0;
  numLabels = nodeLabels.length;
  let currentLabels = {}
  let parent, node, skip;
  for(i = 0; i < numLabels; ++i) {
    skip = false;
    // grad x,y coordinate of node in tree space and check to see if its in the viewing window
    treeX = nodeLabels[i][X];
    treeY = nodeLabels[i][Y];
    if(minX <= treeX && treeX <= maxX &&
        minY <= treeY && treeY <= maxY) {
      node = nodeLabels[i][NODE];
      parent = treeData[node]["parent"];
      while(parent !== "N1") {
        if(parent in currentLabels) {
          skip = true;
        }
        parent = treeData[parent]["parent"];
      }
      if(!skip) {
        // calculate the screen coordinate of the label
        treeSpace = vec4.fromValues(nodeLabels[i][X], nodeLabels[i][Y], 0, 1);
        screenSpace = vec4.create();
        vec4.transformMat4(screenSpace, treeSpace, shaderProgram.mvpMat);
        screenSpace[0] /= screenSpace[3];
        screenSpace[1] /= screenSpace[3];
        pixelX = (screenSpace[0] * 0.5 + 0.5) * canvas.offsetWidth;
        pixelY = (screenSpace[1] * -0.5 + 0.5)* canvas.offsetHeight;

        // make the div
        div = document.createElement("div");

        // assign it a CSS class
        div.className = "floating-div";

        // make a text node for its content
        textNode = document.createTextNode(nodeLabels[i][VALUE]);
        div.appendChild(textNode);

        // add it to the divcontainer
        divContainerElement.appendChild(div);
        div.style.left = Math.floor(pixelX) + "px";
        div.style.top = Math.floor(pixelY) + "px";
        div.id = nodeLabels[i][VALUE];

        // stop once 10 labels have been drawn to screen
        count++;
        currentLabels[node] = null;
      }
      if(count === 10) {
        break;
      }
    }
  }
}

/*
 * Draws the tree
 */
function setPerspective() {
  // create a perspective projection
  let fov = {
    upDegrees: 45,
    downDegrees: 45,
    leftDegrees: 45,
    rightDegrees: 45
  }
  shaderProgram.projMat = mat4.create();
  mat4.perspectiveFromFieldOfView(shaderProgram.projMat, fov,
                   0.1, -10);
}
