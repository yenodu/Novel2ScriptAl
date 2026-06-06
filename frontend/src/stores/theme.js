import { defineStore } from 'pinia'
import { ref } from 'vue'
const THEMES = {
  dark_purple:{name:'暗夜魔典',css:{'--bg-body':'#1E1A2F','--bg-card':'#2A2440','--bg-card-alt':'#352E50','--bg-input':'#1A1628','--bg-code':'#0F0B1E','--code-text':'#e2e8f0','--code-border':'#334155','--bg-modal':'#2A2440','--text-primary':'#E8E0F0','--text-secondary':'#A89BB5','--text-muted':'#7A6D8A','--border':'#3D3560','--border-light':'#4A4168','--accent':'#9b59b6','--accent-hover':'#8E44AD','--accent-light':'#3D2560','--accent-text':'#D4A0F0','--btn-primary-text':'#fff','--danger':'#E74C3C','--success':'#27AE60','--shadow':'rgba(0,0,0,.35)','--table-stripe':'#302544','--tag-bg':'#3D3560','--tag-text':'#C8B8E0'}},
  parchment:{name:'羊皮卷',css:{'--bg-body':'#F5F0E1','--bg-card':'#FFF8EC','--bg-card-alt':'#FDF3E0','--bg-input':'#FFFDF7','--bg-code':'#FDF5E6','--code-text':'#4A3728','--code-border':'#D4C4A8','--bg-modal':'#FFF8EC','--text-primary':'#4A3728','--text-secondary':'#6B5744','--text-muted':'#9B8A78','--border':'#D4C4A8','--border-light':'#E8DCC8','--accent':'#C7B198','--accent-hover':'#B89B7E','--accent-light':'#F0E6D6','--accent-text':'#6B5744','--btn-primary-text':'#4A3728','--danger':'#C0392B','--success':'#6B8E4E','--shadow':'rgba(0,0,0,.08)','--table-stripe':'#FDF3E0','--tag-bg':'#F0E6D6','--tag-text':'#6B5744'}},
  romantic:{name:'浪漫影棚',css:{'--bg-body':'#FFF5F8','--bg-card':'#FFFFFF','--bg-card-alt':'#FFF0F4','--bg-input':'#FFFAFC','--bg-code':'#1A1A2E','--code-text':'#e2e8f0','--code-border':'#334155','--bg-modal':'#FFFFFF','--text-primary':'#2D1B2E','--text-secondary':'#5C3D5E','--text-muted':'#9B7B9E','--border':'#F0C0D0','--border-light':'#F8D8E8','--accent':'#E83E8C','--accent-hover':'#D42A78','--accent-light':'#FDE8F0','--accent-text':'#E83E8C','--btn-primary-text':'#fff','--danger':'#DC3545','--success':'#20C997','--shadow':'rgba(232,62,140,.12)','--table-stripe':'#FFF0F4','--tag-bg':'#FDE8F0','--tag-text':'#E83E8C'}},
  cool_office:{name:'冷静职场',css:{'--bg-body':'#F4F1EA','--bg-card':'#FFFFFF','--bg-card-alt':'#F8F6F2','--bg-input':'#FEFDFB','--bg-code':'#2C3E50','--code-text':'#e2e8f0','--code-border':'#4A6578','--bg-modal':'#FFFFFF','--text-primary':'#2C3E50','--text-secondary':'#5D7A8C','--text-muted':'#8FA0AE','--border':'#D0D8DE','--border-light':'#E2E6EA','--accent':'#5D7A8C','--accent-hover':'#4A6578','--accent-light':'#EEF2F5','--accent-text':'#5D7A8C','--btn-primary-text':'#fff','--danger':'#D9534F','--success':'#4CAF50','--shadow':'rgba(0,0,0,.06)','--table-stripe':'#F8F6F2','--tag-bg':'#EEF2F5','--tag-text':'#5D7A8C'}},
}
const KEY='novel2scriptal-theme'
export const useThemeStore = defineStore('theme',()=>{
  const current=ref(localStorage.getItem(KEY)||'dark_purple')
  function apply(){const t=THEMES[current.value];if(!t)return;Object.entries(t.css).forEach(([k,v])=>document.documentElement.style.setProperty(k,v))}
  function setTheme(k){if(!THEMES[k])return;current.value=k;localStorage.setItem(KEY,k);apply()}
  apply()
  return{current,setTheme,apply,themes:THEMES}
})
