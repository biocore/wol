// urls for webserver
let empress = {}
empress.urls = {
  highlightURL: "http://" + window.location.host + "/highlight",
  collapseURL: "http://" + window.location.host + "/collapse",
  edgeURL: "http://" + window.location.host + "/api/edges",
  colorURL: "http://" + window.location.host + "/color",
  nodeURL: "http://"+ window.location.host + "/api/nodes",
  tableURL: "http://" + window.location.host + "/table_values",
  tableChangeURL: "http://" + window.location.host + "/table_change",
  headersURL: "http://" + window.location.host + "/headers",
  cladeURL: "http://" + window.location.host + "/clades",
  cladeColorURL: "http://" + window.location.host + "/color_clade",
  clearColorCladeURL: "http://" + window.location.host + "/clear_clade",
  subTreeURL: "http://" + window.location.host + "/subtree",
  oldTreeURL: "http://" + window.location.host + "/oldtree",
  selectTreeURL: "http://" + window.location.host + "/select_nodes",
  collapseSTreeURL: "http://" + window.location.host + "/collapse_tree",
  trianglesURL: "http://" + window.location.host + "/api/triangles",
  autoCollapse: 'http://' + window.location.host + '/auto_collapse',
  uncollapseSTreeURL: "http://" + window.location.host + "/uncollapseSTree"

};

// fields to extract from metadata, used in extractInfo()
let field = {
  edgeFields: ["px", "py", "branch_color", "x", "y",
      "branch_color"],
  nodeFields: ["x", "y", "color"],
  triangleFields: ["cx", "cy", "color", "lx", "ly", "color", "rx", "ry", "color"]
};

// stores matrices, and buffers that webgl will uses
let shaderProgram = {};

// the complied vertex/fragment shaders
let gl = {}; // webgl context - used to call webgl functions

// stores info need to draw such as vertex data
let drawingData = {
  isMouseDown: false,
  lastMouseX: null,
  lastMouseY: null,
  zoomAmount: 10,
  currentZoom: 0,
  maxZoom: 30,
  coloredClades: [],
  selectTree: [],
  triangles: []
};

let numAttr = 0;
let attrItem = {};
let grid = {};
let labels = {};
let labelPos = 0;
let gridInfo = {
  initData: [],
  data: [],
  columns: [],
  options: {},
  grid: {}
};
const TRI_PER_ARC = 100;
const ELEMENTS_PER_VERT = 5;
const VERT_PER_TRI = 3;


let numUserSelects = 0;
const CLEAR_COLOR_HEX = "FFFFFF";
const CLEAR_COLOR = 1;
let camera = {};
let shftPress = false;