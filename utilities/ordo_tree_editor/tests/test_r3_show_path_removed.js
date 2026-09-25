const fs=require("fs"), path=require("path");
const base=path.join(__dirname,"..");
const html=fs.readFileSync(path.join(base,"web","index.html"),"utf8");
const app=fs.readFileSync(path.join(base,"web","app.js"),"utf8");
const service=fs.readFileSync(path.join(base,"editor_service.py"),"utf8");
const css=fs.readFileSync(path.join(base,"web","styles.css"),"utf8");
for(const [name,text] of [["html",html],["app",app],["service",service]]){
  for(const token of ["Show Path","show_path","data-workspace-tab=\"paths\"","dialog-panel","canvas-dialog-actions"]){
    if(text.includes(token)){console.error(`Show Path residue in ${name}: ${token}`);process.exit(1);}
  }
}
for(const token of ["path-builder","dialog-playback-controls","dialog-path-edge","dialog-focus-layout"]){if(css.includes(token)){console.error(`Show Path CSS residue: ${token}`);process.exit(1);}}
console.log("PASS Show Path mode fully removed");
