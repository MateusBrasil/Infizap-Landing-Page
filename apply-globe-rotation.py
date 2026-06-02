"""
Substitui o bloco SVG estatico + markers BR/PT por:
- <canvas> + 7 markers (BR, PT, US, GB, NL, CH, SA)
- <script> com land points data + JS de projecao/render/drag
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
HTML = HERE / "infizap-lp-v1.html"
DATA = HERE / "globe-land-data.js"

content = HTML.read_text(encoding="utf-8")

svg_start = content.find('<svg viewBox="0 0 600 600"')
if svg_start < 0:
    print("ERROR: SVG inline not found")
    sys.exit(1)

svg_end = content.find('</svg>', svg_start) + len('</svg>')
pt_marker_start = content.find('data-country="pt"', svg_end)
markers_block_end = content.find('</div>', pt_marker_start) + len('</div>')

print(f"Replacing chars {svg_start}..{markers_block_end} ({markers_block_end - svg_start} chars)")

# Read land data (without the trailing semicolon for cleaner injection)
land_data = DATA.read_text(encoding="utf-8").strip()

MARKERS_HTML = "".join(
    f'<div class="globe-marker-composed" data-country="{cid}" style="opacity:0">'
    f'<span class="globe-pulse-ring"></span>'
    f'<span class="globe-pulse-ring" style="animation-delay:1s"></span>'
    f'<span class="globe-pulse-dot"></span>'
    f'<span class="globe-pulse-label">{label}</span>'
    f'</div>'
    for cid, label in [
        ("br", "Brasil"),
        ("pt", "Portugal"),
        ("us", "Estados Unidos"),
        ("gb", "Inglaterra"),
        ("nl", "Holanda"),
        ("ch", "Suíça"),
        ("sa", "Arábia Saudita"),
    ]
)

CANVAS_HTML = (
    '<canvas id="infizap-globe" class="block h-full w-full select-none" '
    'style="cursor:grab;touch-action:none;border-radius:50%;opacity:0;transition:opacity .6s ease-out" '
    'aria-hidden="true"></canvas>'
)

SCRIPT_JS = """
<script>
""" + land_data + """
(function(){
var wrapper=document.getElementById('infizap-globe-wrapper');
var canvas=document.getElementById('infizap-globe');
if(!canvas||!wrapper||!window.__INFIZAP_LAND_POINTS)return;
var ctx=canvas.getContext('2d');
var LAND=window.__INFIZAP_LAND_POINTS;
var MARKERS=[
{id:'br',lat:-15,lng:-50},
{id:'pt',lat:39.5,lng:-8},
{id:'us',lat:39,lng:-98},
{id:'gb',lat:51.5,lng:-0.13},
{id:'nl',lat:52.37,lng:4.9},
{id:'ch',lat:46.95,lng:7.45},
{id:'sa',lat:24,lng:45}
];
var els={};for(var i=0;i<MARKERS.length;i++){els[MARKERS[i].id]=wrapper.querySelector('[data-country="'+MARKERS[i].id+'"]');}
var CENTER_LAT=15,BASE_LNG=-25,RADIUS_FRAC=0.97;
var phi=0,autoRotate=true,isDragging=false,dragStartX=0,dragStartPhi=0,lastMoveT=0,lastDpr=1;
var cLatR=CENTER_LAT*Math.PI/180,sCLat=Math.sin(cLatR),cCLat=Math.cos(cLatR);
function project(lat,lng,w,h){
var R=Math.min(w,h)/2*RADIUS_FRAC;var cx=w/2,cy=h/2;
var latR=lat*Math.PI/180,lngR=lng*Math.PI/180,cLngR=(BASE_LNG+phi)*Math.PI/180;
var sLat=Math.sin(latR),cLat=Math.cos(latR),dLng=lngR-cLngR,cDL=Math.cos(dLng),sDL=Math.sin(dLng);
var cosC=sCLat*sLat+cCLat*cLat*cDL;
if(cosC<0)return null;
var x=R*cLat*sDL;
var y=-R*(cCLat*sLat-sCLat*cLat*cDL);
return{x:cx+x,y:cy+y,z:cosC};
}
function resize(){
var r=wrapper.getBoundingClientRect();
var dpr=Math.min(window.devicePixelRatio||1,2);lastDpr=dpr;
canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);
canvas.style.width=r.width+'px';canvas.style.height=r.height+'px';
ctx.setTransform(dpr,0,0,dpr,0,0);
}
function render(){
var w=canvas.width/lastDpr,h=canvas.height/lastDpr;
ctx.clearRect(0,0,w,h);
var R=Math.min(w,h)/2*RADIUS_FRAC,cx=w/2,cy=h/2;
var g=ctx.createRadialGradient(cx-R*0.2,cy-R*0.3,0,cx,cy,R);
g.addColorStop(0,'#1a2030');g.addColorStop(0.6,'#0f1320');g.addColorStop(1,'#070a12');
ctx.fillStyle=g;ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.fill();
ctx.fillStyle='rgba(31,217,192,0.05)';ctx.beginPath();ctx.arc(cx,cy,R+6,0,Math.PI*2);ctx.fill();
ctx.fillStyle='rgba(255,255,255,0.55)';ctx.beginPath();
var p;
for(var i=0;i<LAND.length;i++){
p=project(LAND[i][0],LAND[i][1],w,h);
if(p){ctx.moveTo(p.x+1.5,p.y);ctx.arc(p.x,p.y,1.5,0,Math.PI*2);}
}
ctx.fill();
for(var j=0;j<MARKERS.length;j++){
var m=MARKERS[j],el=els[m.id];if(!el)continue;
p=project(m.lat,m.lng,w,h);
if(p){
var fade=Math.min(1,p.z*3);
el.style.left=(p.x/w*100)+'%';
el.style.top=(p.y/h*100)+'%';
el.style.opacity=fade;
}else{el.style.opacity=0;}
}
}
function animate(){
if(autoRotate&&!isDragging)phi+=0.15;
render();requestAnimationFrame(animate);
}
canvas.addEventListener('pointerdown',function(e){isDragging=true;autoRotate=false;dragStartX=e.clientX;dragStartPhi=phi;canvas.style.cursor='grabbing';try{canvas.setPointerCapture(e.pointerId);}catch(_){}});
canvas.addEventListener('pointermove',function(e){if(!isDragging)return;var dx=e.clientX-dragStartX;phi=dragStartPhi+dx*0.4;});
function endDrag(e){if(!isDragging)return;isDragging=false;canvas.style.cursor='grab';try{canvas.releasePointerCapture(e.pointerId);}catch(_){}setTimeout(function(){autoRotate=true;},2000);}
canvas.addEventListener('pointerup',endDrag);
canvas.addEventListener('pointercancel',endDrag);
canvas.addEventListener('pointerleave',endDrag);
if(window.ResizeObserver)new ResizeObserver(resize).observe(wrapper);
window.addEventListener('resize',resize);
resize();animate();
setTimeout(function(){canvas.style.opacity='1';},80);
})();
</script>
"""

new_block = CANVAS_HTML + MARKERS_HTML + SCRIPT_JS

new_content = content[:svg_start] + new_block + content[markers_block_end:]

HTML.write_text(new_content, encoding="utf-8")
print(f"OK. Old length: {len(content)}, new length: {len(new_content)}")
print(f"Replacement size: {len(new_block)} chars")
