class Tree{
  constructor(){
    this.tree = treeData;
    this.root = 'N1';
  }

  order(pre=true, include_self=true){
    let result = [];
    let tmp = [this.root];
    while(tmp.length !== 0){
      let curr = tmp.pop();
      if(include_self || this.root!==curr) result.push(curr);
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
    scale = rescale(height,width);
    centerX = this.tree[this.root].x;
    centerY = this.tree[this.root].y;

    let postorder = order(pre=false, include_self=true);
    for (var i = 0; i < postorder.length; ++i){
        let node = this.tree[postorder[i]];
        node.x = node.x - centerX
        node.y = node.y - centerY
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
    preorder = order(pre=true, include_self=false);
    for(var i = 0; i < preorder.length; ++i){
        let nodeName = preorder[i];
        let node = this.tree[nodeName];
        let parentName = this.tree[nodeName].parent;
        let parent = this.tree[parentName];
        x1 = parent.x;
        y1 = parent.y;

        // init a
        a = parent.angle;

        // same modify across nodes
        a = a - parent.leafcount * da / 2;

        // check for conditional higher order
        for (var i = 0; i < parent.children.length; ++i){
            let sibName = parent.children[i];
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

        result = update_coordinates(
            1.0, 0, 0, direction, angle);

        let x_diff = result.max_x - result.min_x;
        let width_min = 0
        if(x_diff !== 0){
            width_min = float(width) / x_diff;
        }
        let y_diff = result.max_y - result.min_y;
        let height_min = 0
        if(y_diff != 0){
            height_min = float(height) / y_diff;
        }
        let scale = Math.min(width_min, height_min);

        scale *= 0.95
        if(scale > best_scale){
            best_scale = scale;
            mid_x = width / 2 - ((max_x + min_x) / 2) * scale;
            mid_y = height / 2 - ((max_y + min_y) / 2) * scale;
            best_args = { "scale": scale,
                          "mid_x": mid_x,
                          "mid_y": mid_y,
                          "direction": direction,
                          "angle": angle};
        }
    }
    updateCoordinates(best_args.scale,
                       best_args.mid_x,
                       best_args.mid_y,
                       best_args.direction,
                       best_args.angle);
    return best_scale;
  }


}

