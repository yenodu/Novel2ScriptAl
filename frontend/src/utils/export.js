function downloadBlob(content, filename) {
  const blob = new Blob([content], { type: 'application/octet-stream' })
  const url = URL.createObjectURL(blob); const a = document.createElement('a')
  a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url)
}
function parseYaml(yamlStr) {
  try {
    const obj = {}; const lines = yamlStr.split('\n'); let cur = null, dlg = null
    for (const line of lines) {
      if (!line.trim()) continue
      const indent = line.search(/\S/); const t = line.trim()
      if (indent===0 && t.startsWith('title:')) { obj.title = t.slice(6).trim(); continue }
      if (indent===0 && t==='scenes:') { obj.scenes = []; continue }
      if (indent===2 && t.startsWith('- scene_id:')) { cur = { scene_id: parseInt(t.split(':')[1]), dialogues: [] }; obj.scenes.push(cur); continue }
      if (cur && indent===4) {
        if (t.startsWith('heading:')) cur.heading = t.slice(8).trim()
        else if (t.startsWith('action:')) cur.action = t.slice(7).trim()
        else if (t.startsWith('mood:')) cur.mood = t.slice(5).trim()
        else if (t.startsWith('suggested_lighting:')) cur.suggested_lighting = t.slice(19).trim()
        else if (t.startsWith('suggested_sound:')) cur.suggested_sound = t.slice(16).trim()
        else if (t==='dialogues:') {}
        else if (indent===6 && t.startsWith('- character:')) { dlg = { character: t.slice(11).trim(), line: '' }; cur.dialogues.push(dlg) }
        else if (dlg && indent===8 && t.startsWith('line:')) dlg.line = t.slice(5).trim()
      }
    }
    return obj
  } catch { return { title:'Untitled', scenes:[] } }
}
export function yamlToTxt(yamlStr) {
  const obj = parseYaml(yamlStr); const out = [obj.title||'','='.repeat(40),'']
  for (const s of (obj.scenes||[])) {
    out.push(`【${s.heading||'Scene '+s.scene_id}】`,'')
    if (s.action) { out.push(s.action,'') }
    if (s.mood) out.push(`  [情绪:${s.mood}] [灯光:${s.suggested_lighting||'-'}] [音效:${s.suggested_sound||'-'}]`,'')
    for (const d of (s.dialogues||[])) out.push(`  ${d.character}: ${d.line}`)
    out.push('','---','')
  }
  return out.join('\n')
}
export function yamlToFDX(yamlStr) {
  const obj = parseYaml(yamlStr)
  const paras = (obj.scenes||[]).flatMap(s => {
    const items = []
    if (s.heading) items.push(`    <Paragraph Type="Scene Heading"><Text>${esc(s.heading)}</Text></Paragraph>`)
    if (s.action) items.push(`    <Paragraph Type="Action"><Text>${esc(s.action)}</Text></Paragraph>`)
    for (const d of (s.dialogues||[])) { items.push(`    <Paragraph Type="Character"><Text>${esc(d.character||'')}</Text></Paragraph>`); items.push(`    <Paragraph Type="Dialogue"><Text>${esc(d.line||'')}</Text></Paragraph>`) }
    return items
  })
  return ['<?xml version="1.0" encoding="UTF-8"?>','<FinalDraft DocumentType="Script" Template="No" Version="8">','  <Content>',...paras,'  </Content>',`  <TitlePage><Content><Paragraph Type="Title Page"><Text>${esc(obj.title||'')}</Text></Paragraph></Content></TitlePage>`,'</FinalDraft>'].join('\n')
}
function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;') }
export function exportYaml(s) { downloadBlob(s, 'script.yaml') }
export function exportTxt(s) { downloadBlob(yamlToTxt(s), 'script.txt') }
export function exportFdx(s) { downloadBlob(yamlToFDX(s), 'script.fdx') }
