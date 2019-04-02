function constructTree(){
  let tree_fp = "../../../tree.nwk";
  let reader = new FileReader();
  console.log("constructing");
  reader.readAsText(tree_fp);
  reader.onload = () => {
    callback(reader.result);
    console.log(reader.result);
  };
}
parseTree(){


}
