<template>
  <section class="home">
    <div class="panel panel-input">
      <div class="panel-header">
        <h2 class="panel-title">小说内容</h2>
        <div class="style-selector">
          <label class="style-label">风格：</label>
          <select v-model="category" class="select" @change="onCategoryChange"><option v-for="(l,k) in categories" :key="k" :value="k">{{ l }}</option></select>
          <select v-model="store.style" class="select"><option v-for="s in currentSubStyles" :key="s.key" :value="s.key">{{ s.label }}</option></select>
          <label class="mood-toggle"><input type="checkbox" v-model="store.addMood" /><span>情感标签</span></label>
        </div>
      </div>
      <textarea v-model="store.content" class="text-input" placeholder="在此粘贴小说文本……"></textarea>
      <button class="btn-convert" :disabled="store.loading" @click="store.convert()">{{ store.loading ? '转换中…' : '→ 转换' }}</button>
      <p v-if="store.error" class="msg-error">{{ store.error }}</p>
    </div>

    <div class="panel panel-output">
      <div class="panel-header">
        <h2 class="panel-title">剧本 YAML（可编辑）</h2>
        <div class="header-actions">
          <div class="export-dropdown">
            <div v-if="showExport" class="export-menu">
              <button @click="doExport('yaml')">导出 YAML (.yaml)</button>
              <button @click="doExport('txt')">导出 TXT (.txt)</button>
              <button @click="doExport('fdx')">导出 Final Draft (.fdx)</button>
            </div>
          </div>
          <button class="btn-copy" @click="copyYaml">复制</button>
        </div>
      </div>
      <div class="yaml-wrapper">
        <textarea ref="yamlRef" v-model="store.yamlResult" class="yaml-editor" placeholder="转换后的 YAML 剧本将显示在这里……" spellcheck="false" @mouseup="onTextSelect" @keyup="hideFloat"></textarea>
        <button v-if="floatVisible" class="float-btn" :style="floatStyle" @click="openMoodModal">🎭 重新定义情感</button>
      </div>
      <p v-if="!store.yamlResult && !store.loading" class="placeholder-hint">左侧粘贴小说内容，点击「→ 转换」生成 YAML 剧本</p>
    </div>

    <div v-if="showMoodModal" class="modal-overlay" @click.self="showMoodModal=false">
      <div class="mood-modal"><h3>🎭 设置情感标签</h3><p class="mood-context">场景 {{ moodSceneId }}：{{ moodContext }}</p>
        <label class="mood-label">Mood（情绪）</label><input v-model="moodValue" class="mood-input" placeholder="如：紧张、悲伤、温馨…" @keyup.enter="applyMood" />
        <label class="mood-label">灯光（可选）</label><input v-model="moodLighting" class="mood-input" placeholder="如：暖黄顶光" />
        <label class="mood-label">音效（可选）</label><input v-model="moodSound" class="mood-input" placeholder="如：雨声白噪" />
        <div class="mood-actions"><button class="btn-cancel" @click="showMoodModal=false">取消</button><button class="btn-apply" @click="applyMood">应用</button></div>
      </div>
    </div>
    <div v-if="toast" class="toast">{{ toast }}</div>
  </section>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useNovelStore } from '../stores/novel'
import { exportYaml, exportTxt, exportFdx } from '../utils/export'

const store = useNovelStore()
const showExport = ref(false)
function doExport(f) { showExport.value=false; if(!store.yamlResult)return; if(f==='yaml')exportYaml(store.yamlResult);else if(f==='txt')exportTxt(store.yamlResult);else exportFdx(store.yamlResult) }

const categories = { realism:'写实生活化',commercial:'商业化强戏剧',arthouse:'文艺诗意化',fantasy:'奇幻架空类',suspense:'悬疑惊悚',comedy:'喜剧夸张' }
const subStyles = { realism:[{key:'faithful_realism',label:'原著忠实写实'},{key:'slice_of_life',label:'市井烟火写实'},{key:'documentary',label:'纪实改编'}],commercial:[{key:'fast_paced',label:'强爽点浓缩改编'},{key:'family_friendly',label:'合家欢通俗改编'},{key:'crime_thriller',label:'悬疑刑侦商业化'}],arthouse:[{key:'poetic_minimalist',label:'意象留白改编'},{key:'lyrical_prose',label:'抒情散文诗改编'},{key:'absurdist_arthouse',label:'荒诞文艺改编'}],fantasy:[{key:'epic_fantasy',label:'史诗宏大改编'},{key:'light_fantasy',label:'轻量化魔改改编'},{key:'soft_scifi',label:'软科幻落地改编'}],suspense:[{key:'honkaku_mystery',label:'本格推理改编'},{key:'horror_atmosphere',label:'惊悚氛围改编'},{key:'social_suspense',label:'社会派悬疑改编'}],comedy:[{key:'slapstick_absurd',label:'无厘头魔改'},{key:'light_comedy',label:'轻喜剧落地改编'},{key:'satirical_dark',label:'讽刺黑色喜剧'}] }
function findCategory(sk) { for(const[c,l]of Object.entries(subStyles))if(l.some(s=>s.key===sk))return c;return'realism' }
const category = ref(findCategory(store.style))
const currentSubStyles = computed(()=>subStyles[category.value]||subStyles.realism)
function onCategoryChange() { store.style = currentSubStyles.value[0].key }
watch(()=>store.style,v=>{category.value=findCategory(v)})

const yamlRef = ref(null); const floatVisible = ref(false); const floatStyle = ref({})
const showMoodModal = ref(false); const moodSceneId = ref(0); const moodContext = ref('')
const moodValue = ref(''); const moodLighting = ref(''); const moodSound = ref(''); const toast = ref('')
function onTextSelect() {
  const ta = yamlRef.value; if(!ta)return; const s=ta.selectionStart,e=ta.selectionEnd
  if(s===e){floatVisible.value=false;return}
  const text=store.yamlResult,before=text.slice(0,s); const m=before.match(/scene_id:\s*(\d+)/g)
  if(!m){floatVisible.value=false;return}
  moodSceneId.value=parseInt(m[m.length-1].match(/\d+/)[0])
  const ss=before.lastIndexOf(`scene_id: ${moodSceneId.value}`)
  moodContext.value=text.slice(ss,ss+200).split('\n').slice(0,4).join(' ').replace(/\s+/g,' ').slice(0,80)
  const rect=ta.getBoundingClientRect(); const lh=1.7*0.85*16; const lines=before.split('\n').length
  floatStyle.value={top:Math.min(lines*lh,ta.clientHeight-40)+'px',left:(rect.width-160)+'px'}; floatVisible.value=true
}
function hideFloat(){floatVisible.value=false}
function openMoodModal(){floatVisible.value=false;moodValue.value='';moodLighting.value='';moodSound.value='';showMoodModal.value=true;nextTick(()=>document.querySelector('.mood-input')?.focus())}
function applyMood() {
  if(!moodValue.value.trim())return; showMoodModal.value=false; const sid=moodSceneId.value
  let lines=store.yamlResult.split('\n'); let inS=false,insAfter=-1,hasM=false,hasL=false,hasSnd=false,mI=-1,lI=-1,sI=-1
  for(let i=0;i<lines.length;i++) {
    const ln=lines[i]
    if(ln.trimStart().startsWith(`- scene_id: ${sid}`)){inS=true;continue}
    if(inS){if(ln.trimStart().startsWith('- scene_id:'))break; if(ln.trimStart()==='dialogues:'){insAfter=i-1;break}
    if(ln.match(/^\s{4}mood:/)){hasM=true;mI=i}; if(ln.match(/^\s{4}suggested_lighting:/)){hasL=true;lI=i}
    if(ln.match(/^\s{4}suggested_sound:/)){hasSnd=true;sI=i}; insAfter=i}
  }
  if(!inS){_toast('未找到对应场景');return}
  const ind='    '
  if(hasM)lines[mI]=`${ind}mood: ${moodValue.value}`; else{lines.splice(insAfter+1,0,`${ind}mood: ${moodValue.value}`);insAfter++}
  if(moodLighting.value.trim()){if(hasL)lines[lI]=`${ind}suggested_lighting: ${moodLighting.value}`;else{lines.splice(insAfter+1,0,`${ind}suggested_lighting: ${moodLighting.value}`);insAfter++}}
  if(moodSound.value.trim()){if(hasSnd)lines[sI]=`${ind}suggested_sound: ${moodSound.value}`;else{lines.splice(insAfter+1,0,`${ind}suggested_sound: ${moodSound.value}`);insAfter++}}
  store.yamlResult=lines.join('\n'); _toast(`✅ 场景 ${sid} 情感已更新为「${moodValue.value}」`)
}
function _toast(msg){toast.value=msg;setTimeout(()=>{toast.value=''},2500)}
async function copyYaml(){if(!store.yamlResult)return;try{await navigator.clipboard.writeText(store.yamlResult)}catch{}}
</script>

<style scoped>
.home{display:flex;gap:1.5rem;align-items:flex-start}
.panel{flex:1;min-width:0;background:var(--bg-card);border-radius:10px;padding:1.5rem;box-shadow:0 1px 3px var(--shadow);display:flex;flex-direction:column}
.panel-output{border-left:4px solid var(--accent)}
.panel-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem}
.panel-title{font-size:1rem;font-weight:600;color:var(--text-primary);margin:0}
.style-selector{display:flex;align-items:center;gap:.25rem}
.style-label{font-size:.85rem;color:var(--text-secondary)}
.select{padding:.25rem .5rem;border:1px solid var(--border);border-radius:4px;font-size:.85rem;cursor:pointer;background:var(--bg-card);color:var(--text-primary)}
.select:focus{outline:none;border-color:var(--accent)}
.mood-toggle{display:flex;align-items:center;gap:.3rem;font-size:.85rem;color:var(--text-secondary);cursor:pointer;white-space:nowrap}
.mood-toggle input{cursor:pointer}
.text-input,.yaml-editor{flex:1;width:100%;padding:.75rem;font-size:.9rem;border-radius:6px;resize:none;line-height:1.7;min-height:420px}
.text-input{font-family:inherit;background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border)}
.text-input:focus{outline:none;border-color:var(--accent)}
.yaml-editor{font-family:'Cascadia Code','Fira Code','Consolas',monospace;color:var(--code-text);background:var(--bg-code);border:1px solid var(--code-border);tab-size:2}
.yaml-editor:focus{outline:none;border-color:var(--accent)}
.yaml-editor::placeholder{color:var(--text-muted);font-family:inherit}
.btn-convert{margin-top:.75rem;padding:.6rem 0;width:100%;font-size:1rem;font-weight:600;color:var(--btn-primary-text);background:var(--accent);border:none;border-radius:6px;cursor:pointer}
.btn-convert:hover:not(:disabled){background:var(--accent-hover)}
.btn-convert:disabled{opacity:.6;cursor:not-allowed}
.header-actions{display:flex;gap:.5rem;align-items:center}
.export-dropdown{position:relative}
.btn-export{padding:.25rem .75rem;font-size:.8rem;color:var(--text-secondary);background:var(--bg-card);border:1px solid var(--border);border-radius:4px;cursor:pointer}
.btn-export:hover{border-color:var(--accent);color:var(--accent)}
.export-menu{position:absolute;top:100%;right:0;margin-top:4px;background:var(--bg-card);border:1px solid var(--border-light);border-radius:6px;box-shadow:0 4px 12px var(--shadow);z-index:50;min-width:180px;overflow:hidden}
.export-menu button{display:block;width:100%;padding:.5rem .75rem;border:none;background:transparent;font-size:.8rem;color:var(--text-primary);cursor:pointer;text-align:left}
.export-menu button:hover{background:var(--bg-card-alt);color:var(--accent)}
.btn-copy{padding:.25rem .75rem;font-size:.8rem;color:var(--accent);background:var(--accent-light);border:1px solid var(--accent-light);border-radius:4px;cursor:pointer}
.btn-copy:hover{background:var(--accent-hover)}
.msg-error{margin-top:.5rem;color:var(--danger);font-size:.85rem;flex-shrink:0}
.placeholder-hint{margin-top:.5rem;color:var(--text-muted);font-size:.8rem;text-align:center;flex-shrink:0}
.yaml-wrapper{position:relative}
.float-btn{position:absolute;padding:.4rem .8rem;font-size:.8rem;color:#fff;background:var(--accent);border:none;border-radius:6px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.25);z-index:10;animation:fadeUp .2s}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);display:flex;justify-content:center;align-items:center;z-index:100}
.mood-modal{background:var(--bg-card);border-radius:12px;padding:1.75rem;width:90%;max-width:420px;box-shadow:0 8px 32px var(--shadow)}
.mood-modal h3{font-size:1.1rem;margin-bottom:.5rem;color:var(--text-primary)}
.mood-context{font-size:.8rem;color:var(--text-muted);margin-bottom:1rem;padding:.4rem .6rem;background:var(--bg-card-alt);border-radius:4px}
.mood-label{display:block;font-size:.8rem;color:var(--text-secondary);margin:.5rem 0 .2rem}
.mood-input{width:100%;padding:.45rem .6rem;border:1px solid var(--border);border-radius:6px;font-size:.9rem;background:var(--bg-input);color:var(--text-primary)}
.mood-input:focus{outline:none;border-color:var(--accent)}
.mood-actions{display:flex;gap:.5rem;justify-content:flex-end;margin-top:1rem}
.btn-cancel{padding:.4rem 1rem;font-size:.85rem;color:var(--text-secondary);background:var(--bg-card-alt);border:1px solid var(--border-light);border-radius:6px;cursor:pointer}
.btn-apply{padding:.4rem 1rem;font-size:.85rem;color:var(--btn-primary-text);background:var(--accent);border:none;border-radius:6px;cursor:pointer}
.toast{position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);padding:.6rem 1.5rem;background:var(--bg-card);color:var(--text-primary);border:1px solid var(--border);border-radius:8px;font-size:.9rem;z-index:200;animation:fadeUp .3s}
</style>
