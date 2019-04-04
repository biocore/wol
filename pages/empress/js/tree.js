class Tree{
  constructor(tree_nwk, edgeData, metadata, m_headers, max){
    this.tree = tree_nwk;
    this.edgeData = edgeData;
    this.metadata = metadata;
    this.m_headers = m_headers;
    this.max = max;
    this.root = 'N1';
    this.numBranches = Object.keys(metadata).length;
    this.triData = [];
    this.triRoots = [];
  }

  order(pre, start, include_self){
    let result = [];
    let tmp = [start];
    while(tmp.length !== 0){
      let curr = tmp.pop();
      if(include_self || start!==curr) result.push(curr);
      for (var i = 0; i < this.tree[curr].children.length; ++i){
        tmp.push(this.tree[curr].children[i]);
      }
    }
    if(pre){
      return result;
    }
    else{
      return result.reverse();
    }
  }

  coords(height, width){
    let scale = this.rescale(height,width);
    let centerX = this.tree[this.root].x;
    let centerY = this.tree[this.root].y;

    let postorder = this.order(false, 'N1', true);
    for (var i = 0; i < postorder.length; ++i){
        let node = this.tree[postorder[i]];
        node.x = node.x - centerX;
        node.y = node.y - centerY;
    }
  }

  updateCoordinates(s, x1, y1, a, da){
    let max_x = Number.MIN_VALUE;
    let min_x = Number.MAX_VALUE;
    let max_y = Number.MIN_VALUE;
    let min_y = Number.MAX_VALUE;

    //calculates self coords/angle
    //Constant angle algorithm.  Should add maximum daylight step.
    let length = this.tree[this.root].length;
    let x2 = x1 + length * s * Math.sin(a);
    let y2 = y1 + length * s * Math.cos(a);
    this.tree[this.root].x = x2;
    this.tree[this.root].y = y2;
    this.tree[this.root].angle = a;
    let preorder = this.order(true, 'N1', false);

    for(var i = 0; i < preorder.length; ++i){
        let nodeName = preorder[i];
        let node = this.tree[nodeName];
        let parentName = node.parent;
        let parent = this.tree[parentName];
        x1 = parent.x;
        y1 = parent.y;

        // init a
        a = parent.angle;

        // same modify across nodes
        a = a - parent.leafcount * da / 2;

        // check for conditional higher order
        for (var j = 0; j < parent.children.length; ++j){
            let sibName = parent.children[j];
            let sib = this.tree[sibName];
            if(sibName != nodeName){
                a += sib.leafcount * da
            } else {
                a += (node.leafcount * da) / 2;
                break;
            }
        }
        // Constant angle algorithm.  Should add maximum daylight step.
        x2 = x1 + node.length * s * Math.sin(a);
        y2 = y1 + node.length * s * Math.cos(a);
        node.x = x2;
        node.y = y2;
        node.angle = a;

        max_x = Math.max(max_x, x2);
        min_x = Math.min(min_x, x2);
        max_y = Math.max(max_y, y2);
        min_y = Math.min(min_y, y2);

    }
    return {"max_x": max_x,
            "min_x": min_x,
            "max_y": max_y,
            "min_y": min_y};
  }

  rescale(height, width){
    let angle = (2 * Math.PI) / this.tree[this.root].leafcount;

    let best_scale = 0;
    let best_args = {};
    for(var i = 0; i < 60; ++i){
        let direction = i / 60.0 * Math.PI;
        let result = this.updateCoordinates(
            1.0, 0, 0, direction, angle);

        let x_diff = result.max_x - result.min_x;
        let width_min = 0
        if(x_diff !== 0){
            width_min = width / x_diff;
        }
        let y_diff = result.max_y - result.min_y;
        let height_min = 0
        if(y_diff != 0){
            height_min = height / y_diff;
        }
        let scale = Math.min(width_min, height_min);

        scale *= 0.95
        if(scale > best_scale){
            best_scale = scale;
            let mid_x = width / 2 - ((result.max_x + result.min_x) / 2) * scale;
            let mid_y = height / 2 - ((result.max_y + result.min_y) / 2) * scale;
            best_args = { "scale": scale,
                          "mid_x": mid_x,
                          "mid_y": mid_y,
                          "direction": direction,
                          "angle": angle};
        }
    }
    this.updateCoordinates(best_args.scale,
                       best_args.mid_x,
                       best_args.mid_y,
                       best_args.direction,
                       best_args.angle);
    return best_scale;
  }

  collapse(taxLevel) {
    const RED = 0.73828125;
    const GREEN = 0.73828125;
    const BLUE = 0.73828125;
    let preorder = this.order(true, this.root, false);
    let i;
    let collapsedNodes = 0;
    let node;
    let rootNode;
    let rx, ry, tlX, tlY, trX, trY, theta;
    this.triData = [];
    this.triRoots = [];
    for(i = 0; i < preorder.length; i++) {
        this.metadata[preorder[i]]['branch_is_visible'] = true;
    }
    for(node in this.metadata) {
        if(this.metadata[node]["d_" + taxLevel] != null) {
            preorder = this.order(true, node, false);
            for(i = 0; i < preorder.length; i++) {
                this.metadata[preorder[i]]['branch_is_visible'] = false;
                collapsedNodes += 1;
            }
            rootNode = this.tree[node];
            theta = rootNode['starting_angle'];
            rx = rootNode["x"];
            ry = rootNode["y"];
            tlX = rootNode["largest_branch"] * Math.cos(theta) + rx;
            tlY = rootNode["largest_branch"] * Math.sin(theta) + ry;
            theta += rootNode["theta"];
            trX = rootNode["smallest_branch"] * Math.cos(theta) + rx;
            trY = rootNode["smallest_branch"] * Math.sin(theta) + ry;
            this.triData.push(rx);
            this.triData.push(ry);
            this.triData.push(RED);
            this.triData.push(GREEN);
            this.triData.push(BLUE);
            this.triData.push(tlX);
            this.triData.push(tlY);
            this.triData.push(RED);
            this.triData.push(GREEN);
            this.triData.push(BLUE);
            this.triData.push(trX);
            this.triData.push(trY);
            this.triData.push(RED);
            this.triData.push(GREEN);
            this.triData.push(BLUE);
            this.triRoots.push(node);
        }
    }
    this.updateEdgeData(collapsedNodes);
    return this.edgeData;
  }

  uncollapse() {
    let preorder = this.order(true, this.root, false);
    let i;
    let collapsedNodes = 0;
    const NON_HIDDEN = 0
    this.triData = [];
    this.triRoots = [];
    for(i = 0; i < preorder.length; i++) {
        this.metadata[preorder[i]]['branch_is_visible'] = true;
    }
    this.updateEdgeData(NON_HIDDEN);
    return this.edgeData;
  }

  updateEdgeData(numNotVis) {
    let i = 0;
    let node;
    const VERT_SIZE = 10;
    const PX = 0;
    const PY = 1;
    const PR = 2;
    const PG = 3;
    const PB = 4;
    const X = 5;
    const Y = 6;
    const R = 7;
    const G = 8;
    const B = 9;
    const RED = 0;
    const GREEN = 1;
    const BLUE = 2;
    let nodeMetadata;
    this.edgeData = new Array((this.numBranches - numNotVis) * VERT_SIZE);
    for(node in this.metadata) {
        nodeMetadata = this.metadata[node];
        if(nodeMetadata['branch_is_visible']) {
            this.edgeData[i + PX] = nodeMetadata["px"];
            this.edgeData[i + PY] = nodeMetadata["py"];
            this.edgeData[i + PR] = nodeMetadata["branch_color"][RED];
            this.edgeData[i + PG] = nodeMetadata["branch_color"][GREEN];
            this.edgeData[i + PB] = nodeMetadata["branch_color"][BLUE];
            this.edgeData[i + X] = nodeMetadata["x"];
            this.edgeData[i + Y] = nodeMetadata["y"];
            this.edgeData[i + R] = nodeMetadata["branch_color"][RED];
            this.edgeData[i + G] = nodeMetadata["branch_color"][GREEN]
            this.edgeData[i + B] = nodeMetadata["branch_color"][BLUE]
            i += VERT_SIZE;
        }
    }
  }

  getTaxonLabels(taxLevel, tips) {
    let labels = [];
    let node;
    for(node in this.metadata) {
      if(this.metadata[node][taxLevel] != null && this.tree[node]["is_tip"] === tips) {
        labels.push([this.metadata[node]["x"],
                         this.metadata[node]["y"],
                         this.metadata[node][taxLevel],
                         this.tree[node]["leafcount"],
                         node]);
      }
    }
    labels.sort(function (dataRow1, dataRow2) {
      if(dataRow1[3] < dataRow2[3] ) {
        return 1;
      }
      return -1;
    });
    return labels;
  }

  triangleAt(x,y) {
    let triangle = {}, a = {}, b = {}, c = {}, result = {};
    let i = 0;
    const CX = 0;
    const CY = 1;
    const LX = 5;
    const LY = 6;
    const RX = 10;
    const RY = 11;
    const TRI_SIZE = 15;
    while(i < this.triData.length) {
        a.x = this.triData[i + CX];
        a.y = this.triData[i + CY];
        b.x = this.triData[i + LX];
        b.y = this.triData[i + LY];
        c.x = this.triData[i + RX];
        c.y = this.triData[i + RY];
        triangle.area = this.triangleArea(a, b, c);
        triangle.s1 = this.triangleArea({'x': x, 'y': y}, b, c);
        triangle.s2 = this.triangleArea(a, {'x': x, 'y': y}, c);
        triangle.s3 = this.triangleArea(a, b, {'x': x, 'y': y});
        if(Math.abs(triangle.area - triangle.s1 - triangle.s2 - triangle.s3) < 0.0001) {
            return this.triRoots[i / TRI_SIZE];
        }
        i += TRI_SIZE;
    }
    return null;
  }

  triangleArea(a, b, c) {
    return Math.abs((a.x*(b.y - c.y) + b.x*(c.y - a.y) + c.x*(a.y - b.y)) / 2)
  }
}
