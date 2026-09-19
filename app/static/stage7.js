
(function(){
  const $=(s,r=document)=>r.querySelector(s);
  const esc=s=>String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));
  const signs=["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya","Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"];
  const abbr={Surya:"Su",Chandra:"Mo",Mangala:"Ma",Budha:"Me",Guru:"Ju",Shukra:"Ve",Shani:"Sa",Rahu:"Ra",Ketu:"Ke"};
  function drawKundli(chart){
    const W=480,S=120;
    const pts=[];
    Object.entries(chart.grahas||{}).forEach(([name,p])=>{
      pts.push({name,sign:Math.floor((p.longitude||0)/30),deg:p.degree_in_rashi||0});
    });
    const asc=chart.lagna?.rashi, ascI=signs.indexOf(asc);
    let svg=`<svg class="kundli" viewBox="0 0 480 480" aria-label="North Indian style Rashi Kundli">
      <rect x="1" y="1" width="478" height="478" class="house"/>
      <path d="M1 1L479 479M479 1L1 479M240 1V479M1 240H479" class="diag"/>
      <path d="M1 1L240 240L479 1M1 479L240 240L479 479" class="diag"/>`;
    // Four corner/side house triangles are implied by the North Indian diamond geometry.
    for(let i=0;i<12;i++){
      const x=[120,240,360,120,240,360,120,240,360,120,240,360][i];
      const y=[72,48,72,168,168,168,312,312,312,408,432,408][i];
      svg+=`<text x="${x}" y="${y}" text-anchor="middle" class="sign">${i===0&&ascI>=0?esc(signs[ascI]):""}</text>`;
    }
    const buckets=Array.from({length:12},()=>[]);
    pts.forEach(p=>buckets[p.sign].push(`${abbr[p.name]||p.name.slice(0,2)}`));
    for(let i=0;i<12;i++){
      const labels=buckets[i].join(" ");
      const house=ascI>=0?((i-ascI+12)%12)+1:null;
      const x=[120,240,360,80,240,400,120,240,360,80,240,400][i];
      const y=[112,78,112,208,208,208,292,292,292,372,402,372][i];
      svg+=`<text x="${x}" y="${y}" text-anchor="middle" class="planet">${esc(labels)}</text>${house?`<text x="${x}" y="${y+16}" text-anchor="middle" class="sign">H${house}</text>`:""}`;
    }
    svg+=`</svg>`;
    return svg;
  }
  window.BhawishyaStage7={drawKundli};
})();
