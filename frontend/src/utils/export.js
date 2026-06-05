// ---- helper: download Blob ----
function downloadBlob(content, filename) {
  const blob = new Blob([content], { type: 'application/octet-stream' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// ---- parse YAML string to object ----
function parseYaml(yamlStr) {
  try {
    const obj = {}
    const lines = yamlStr.split('\n')
    let currentScene = null
    let currentDialogue = null
    let inDialogues = false

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      if (!line.trim()) continue

      const indent = line.search(/\S/)
      const trimmed = line.trim()

      // title
      if (indent === 0 && trimmed.startsWith('title:')) {
        obj.title = trimmed.slice(6).trim()
        continue
      }

      // scenes array start
      if (indent === 0 && trimmed === 'scenes:') {
        obj.scenes = []
        continue
      }

      // scene item
      if (indent === 2 && trimmed.startsWith('- scene_id:')) {
        currentScene = { scene_id: parseInt(trimmed.split(':')[1]), dialogues: [] }
        obj.scenes.push(currentScene)
        inDialogues = false
        continue
      }

      if (currentScene && indent === 4) {
        if (trimmed.startsWith('heading:')) {
          currentScene.heading = trimmed.slice(8).trim()
        } else if (trimmed.startsWith('action:')) {
          currentScene.action = trimmed.slice(7).trim()
          // action may span multiple lines
        } else if (trimmed.startsWith('mood:')) {
          currentScene.mood = trimmed.slice(5).trim()
        } else if (trimmed.startsWith('suggested_lighting:')) {
          currentScene.suggested_lighting = trimmed.slice(19).trim()
        } else if (trimmed.startsWith('suggested_sound:')) {
          currentScene.suggested_sound = trimmed.slice(16).trim()
        } else if (trimmed === 'dialogues:') {
          inDialogues = true
        } else if (indent === 6 && trimmed.startsWith('- character:')) {
          currentDialogue = { character: trimmed.slice(11).trim(), line: '' }
          currentScene.dialogues.push(currentDialogue)
        } else if (currentDialogue && indent === 8 && trimmed.startsWith('line:')) {
          currentDialogue.line = trimmed.slice(5).trim()
        }
      }
    }
    return obj
  } catch {
    return { title: 'Untitled', scenes: [] }
  }
}

// ---- YAML → readable TXT ----
export function yamlToTxt(yamlStr) {
  const obj = parseYaml(yamlStr)
  const lines = []

  lines.push(obj.title || 'Untitled')
  lines.push('='.repeat(40))
  lines.push('')

  for (const s of (obj.scenes || [])) {
    lines.push(`【${s.heading || 'Scene ' + s.scene_id}】`)
    lines.push('')
    if (s.action) { lines.push(s.action); lines.push('') }
    if (s.mood) { lines.push(`  [情绪: ${s.mood}]  [灯光: ${s.suggested_lighting || '-'}]  [音效: ${s.suggested_sound || '-'}]`); lines.push('') }
    for (const d of (s.dialogues || [])) {
      lines.push(`  ${d.character}: ${d.line}`)
    }
    lines.push('')
    lines.push('---')
    lines.push('')
  }

  return lines.join('\n')
}

// ---- YAML → Final Draft FDX ----
export function yamlToFDX(yamlStr) {
  const obj = parseYaml(yamlStr)
  const title = obj.title || 'Untitled'
  const scenes = obj.scenes || []

  const paragraphs = scenes.flatMap(s => {
    const items = []
    // Scene Heading
    if (s.heading) {
      items.push(`    <Paragraph Type="Scene Heading"><Text>${esc(s.heading)}</Text></Paragraph>`)
    }
    // Action
    if (s.action) {
      items.push(`    <Paragraph Type="Action"><Text>${esc(s.action)}</Text></Paragraph>`)
    }
    // Dialogues
    for (const d of (s.dialogues || [])) {
      const char = d.character || 'UNKNOWN'
      const line = d.line || ''
      items.push(`    <Paragraph Type="Character"><Text>${esc(char)}</Text></Paragraph>`)
      items.push(`    <Paragraph Type="Dialogue"><Text>${esc(line)}</Text></Paragraph>`)
    }
    return items
  })

  const fdx = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<FinalDraft DocumentType="Script" Template="No" Version="8">',
    '  <Content>',
    ...paragraphs,
    '  </Content>',
    `  <TitlePage><Content><Paragraph Type="Title Page"><Text>${esc(title)}</Text></Paragraph></Content></TitlePage>`,
    '</FinalDraft>',
  ].join('\n')

  return fdx
}

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

// ---- export actions ----
export function exportYaml(yamlStr) {
  downloadBlob(yamlStr, 'script.yaml')
}

export function exportTxt(yamlStr) {
  downloadBlob(yamlToTxt(yamlStr), 'script.txt')
}

export function exportFdx(yamlStr) {
  downloadBlob(yamlToFDX(yamlStr), 'script.fdx')
}
