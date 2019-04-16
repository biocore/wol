class Tree{
  constructor(tree_nwk, edgeData, metadata, m_headers, maxes){
    this.tree = tree_nwk;
    this.edgeData = edgeData;
    this.metadata = metadata;
    this.m_headers = m_headers;
    this.max = maxes.dim;
    this.maxes = maxes;
    this.root = 'N1';
    this.numBranches = Object.keys(metadata).length;
    this.triData = [];
    this.triRoots = [];
    this.lastHighTri = 0;
  }

  order(pre, start, include_self, tip=false){
    let result = [];
    let tmp = [start];
    while(tmp.length !== 0){
      let curr = tmp.pop();
      if(include_self || start!==curr) {
        if (!tip || this.tree[curr].is_tip == "true"){
            result.push(curr);
        }
      }
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

  collapse(taxLevel, taxPrefix) {
    const RED = 0;
    const GREEN = 1;
    const BLUE = 2;
    let r, g, b;
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
        if(this.metadata[node][taxPrefix + taxLevel] != null) {
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
            r = this.metadata[node]['branch_color'][RED];
            g = this.metadata[node]['branch_color'][GREEN];
            b = this.metadata[node]['branch_color'][BLUE];
            this.triData.push(rx);
            this.triData.push(ry);
            this.triData.push(r);
            this.triData.push(g);
            this.triData.push(b);
            this.triData.push(tlX);
            this.triData.push(tlY);
            this.triData.push(r);
            this.triData.push(g);
            this.triData.push(b);
            this.triData.push(trX);
            this.triData.push(trY);
            this.triData.push(r);
            this.triData.push(g);
            this.triData.push(b);
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
    this.edgeData = new Array((this.numBranches ) * VERT_SIZE);
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

  getTaxonLabels(taxLevel, tips, taxPrefix, sort) {
    let labels = [];
    let node;
    for(node in this.metadata) {
      if(this.metadata[node][taxPrefix + taxLevel] != null
            && this.tree[node]["is_tip"] === tips
            && this.metadata[node]["branch_is_visible"]) {
        labels.push([this.metadata[node]["x"],
                         this.metadata[node]["y"],
                         this.metadata[node][taxLevel],
                         this.tree[node]["leafcount"],
                         node]);
      }
    }
    labels.sort(sort);
    return labels;
  }

  triangleAt(x,y) {
    const TRI_SIZE = 15;
    const CX = 0, CY = 1, LX = 5, LY = 6, RX = 10, RY = 11;
    let i = 0;
    let triangle = {}, a = {}, b = {}, c = {}, result = {};
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
            result.id = this.triRoots[i / TRI_SIZE];
            result.tri = this.setTriHighlight(i);
            return result;
        }
        i += TRI_SIZE;
    }
    return null;
  }

  setTriHighlight(idx) {
    const TRI_SIZE = 15;
    const CX = 0, CY = 1, LX = 5, LY = 6, RX = 10, RY = 11;
    const CR = 2, CG = 3, CB = 4, LR = 7, LG = 8, LB = 9, RR = 12, RG = 13, RB = 14;
    const RED = 0.62890625, GREEN = 0.84765625, BLUE = 0.60546875;
    let tri = new Array(TRI_SIZE);
    tri[CX] = this.triData[idx + CX];
    tri[CY] = this.triData[idx + CY];
    tri[CR] = RED;
    tri[CG] = GREEN;
    tri[CB] = BLUE;
    tri[LX] = this.triData[idx + LX];
    tri[LY] = this.triData[idx + LY];
    tri[LR] = RED;
    tri[LG] = GREEN;
    tri[LB] = BLUE;
    tri[RX] = this.triData[idx + RX];
    tri[RY] = this.triData[idx + RY];
    tri[RR] = RED;
    tri[RG] = GREEN;
    tri[RB] = BLUE;
    return tri;
  }
  triangleArea(a, b, c) {
    return Math.abs((a.x*(b.y - c.y) + b.x*(c.y - a.y) + c.x*(a.y - b.y)) / 2)
  }

  colorBranches(category) {
    let i = 0;
    let result = {};
    if(category === "default") {
        let color = this.getDefaultColor();
        for(i in this.metadata) {
            this.metadata[i]['branch_color'] = color;
        }
    }
    else {
        let keyInfo = {};
        if(category === "(preset)"){
            let value, color;
            for(i in this.metadata) {
                value = this.metadata[i]["color_pal"];
                color = this.getColorPal(value);
                keyInfo[value] = this.getColorHexCode(color);
                this.metadata[i]['branch_color'] = color;
            }
        }
        else {
            let min = this.maxes[category][0];
            let max = this.maxes[category][1];
            keyInfo = {
                "min": [min, this.getColorHexCode(this.getColor(min, max, min))],
                "max": [max, this.getColorHexCode(this.getColor(min, max, max))]
            };
            for (i in this.metadata) {
                if(this.metadata[i][category] !== null){
                    this.metadata[i]['branch_color'] = this.getColor(min, max, this.metadata[i][category]);
                }
            }
        }
        result["keyInfo"] = keyInfo;
    }
    this.updateEdgeData(0);
    result["edgeData"] = this.edgeData;
    return result;
  }
  getColorHexCode(colorArray) {
    const RED = 0, GREEN = 1, BLUE = 2, BASE_HEX = 16, LARGEST_COLOR = 256;
    let hexString = (colorArray[RED] * LARGEST_COLOR).toString(BASE_HEX)
        + (colorArray[GREEN] * LARGEST_COLOR).toString(BASE_HEX)
        + (colorArray[BLUE] * LARGEST_COLOR).toString(BASE_HEX);
    return (hexString.length < 6) ? hexString + "0" : hexString;
  }
  getDefaultColor() {
    return [0.7, 0.7, 0.7];
  }
  getColor(min, max, val) {
    //n red
    // let bucketSize = (max - min) / 9;
    // if(val < min + bucketSize) {
    //     return [0.99609375, 0.95703125, 0.91796875];
    // }
    // else if(val < min + 2*bucketSize) {
    //     return [0.9921875, 0.8984375, 0.8046875];
    // }
    // else if(val < min + 3*bucketSize) {
    //     return [0.98828125, 0.8125, 0.6328125];
    // }
    // else if(val < min + 4*bucketSize) {
    //     return [98828125, 0.6796875, 0.41796875];
    // }
    // else if(val < min + 5*bucketSize) {
    //     return [0.98828125, 0.55078125, 0.234375];
    // }
    // else if(val < min + 6*bucketSize) {
    //     return [0.94140625, 0.41015625, 0.07421875];
    // }
    // else if(val < min +  7*bucketSize) {
    //     return [0.84765625, 0.28125, 0.00390625];
    // }
    // else if(val < min + 8*bucketSize) {
    //     return [0.6484375, 0.2109375, 0.01171875];
    // }
    // return [0.49609375, 0.15234375, 0.015625];

    // yellow red
    // console.log( min + 6&bucketSize)
    let bucketSize = (max - min) / 5;
    if(val < min + bucketSize) {
        return [0.9921875, 0.84765625, 0.4609375];
    }
    else if(val < min + 2*bucketSize) {
        return [0.9921875, 0.6953125, 0.296875];
    }
    else if(val < min + 3*bucketSize) {
        return [0.98828125, 0.55078125, 0.234375];
    }
    else if(val < min + 4*bucketSize) {
        return [0.984375, 0.3046875, 0.1640625];
    }
    // else if(val < min + 5*bucketSize) {
        return [0.88671875, 0.1015625, 0.109375];
    // }
    // else if(val < min + 6*bucketSize) {
    //     return [0.73828125, 0.0, 0.1484375];
    // }
    // return [0.5, 0.0, 0.1484375];

  }

  getColorPal(val) {
    let colors = {
        'Eukaryota': [0.94140625, 0.90234375, 0.609375],
        'Archaea': [0.65625, 0.62109375, 0.7890625],
        'Asgard': [0.44140625, 0.33984375, 0.625],
        'TACK': [0.74609375, 0.53515625, 0.6328125],
        'Crenarchaeota': [0.578125, 0.35546875, 0.58984375],
        'Euryarchaeota': [0.55078125, 0.48828125, 0.765625],
        'DPANN': [0.41015625, 0.375, 0.55859375],
        'CPR': [0.9140625, 0.75390625, 0.72265625],
        'Microgenomates': [0.8828125, 0.53125, 0.57421875],
        'Parcubacteria': [0.88671875, 0.62109375, 0.515625],
        'Eubacteria': [0.6875, 0.875, 0.87890625],
        'Terrabacteria': [0.625, 0.71484375, 0.875],
        'Actinobacteria': [0.48828125, 0.55859375, 0.78125],
        'Firmicutes': [0.12109375, 0.19140625, 0.46484375],
        'Chloroflexi': [0.28125, 0.37890625, 0.6953125],
        'Cyanobacteria': [0.34765625, 0.55859375, 0.875],
        'Spirochaetes': [0.44140625, 0.609375, 0.6875],
        'PVC': [0.78125, 0.83984375, 0.8125],
        'Chlamydiae': [0.6015625, 0.75390625, 0.7265625],
        'FCB': [0.66796875, 0.82421875, 0.90625],
        'Bacteroidetes': [0.38671875, 0.65625, 0.828125],
        'Proteobacteria': [0.31640625, 0.45703125, 0.62109375]
    }
    return colors[val];
  }

  getGenomeIDs(nodeId){
    let node = this.tree[nodeId];
    // If the node is a tip
    if(node.children.length == 0){
      return [nodeId];
    } else {
      return this.order(true, nodeId, false, true);
    }
  }

  /**
   * Generate newick format string based on the subtree rooted at nodeId
   */
  toNewick(nodeId){
    let node = this.tree[nodeId];
    let result = [];
    let resultStr = nodeId + ":" + node.length;
    // Base case
    if (node.children.length == 0) return resultStr;
    for (var i = 0; i < node.children.length; i++){
      let child = node.children[i];
      result.push(this.toNewick(child));
    }
    return '(' + result.join(',') + ')' + resultStr;
  }

}
