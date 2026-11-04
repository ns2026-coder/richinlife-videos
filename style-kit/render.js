const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
(async()=>{const b=await chromium.launch();const P=await b.newPage({viewport:{width:1080,height:1920}});await P.goto('file://'+__dirname+'/reference_fee_scenes.html');await P.evaluate(()=>document.fonts.load('800 60px Poppins'));await P.waitForTimeout(400);
const cuts=[0,2.3,6,11,19.9,24.3,31.4,39.9,46,52.6,63];let list='';
for(let i=0;i<cuts.length-1;i++){const tmp=`sc${i}.tmp.mp4`,fin=`sc${i}.mp4`;const f=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-crf','20','-preset','veryfast','-pix_fmt','yuv420p',tmp],{stdio:['pipe','inherit','inherit']});
 const a=Math.round(cuts[i]*30),z=Math.round(cuts[i+1]*30);for(let n=a;n<z;n++){await P.evaluate(t=>draw(t),n/30);const j=await P.screenshot({type:'jpeg',quality:92});if(!f.stdin.write(j))await new Promise(r=>f.stdin.once('drain',r))}
 f.stdin.end();await new Promise((r,e)=>f.on('close',c=>c?e(c):r()));fs.renameSync(tmp,fin);list+=`file ${fin}\n`;console.log(i)}
fs.writeFileSync('list.txt',list);await b.close()})()
