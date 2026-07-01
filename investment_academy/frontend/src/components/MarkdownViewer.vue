<template>
  <div class="markdown-content" v-html="rendered"></div>
</template>

<script>
import { marked } from 'marked'

export default {
  name: 'MarkdownViewer',
  props: {
    content: { type: String, default: '' }
  },
  computed: {
    rendered() {
      if (!this.content) return ''
      return marked(this.content, {
        breaks: true,
        gfm: true,
      })
    }
  },
}
</script>

<style>
/* Markdown 内容样式 — 全局生效（scoped 无法作用于 v-html） */
.markdown-content h1 { font-size: 1.6rem !important; }
.markdown-content h2 { font-size: 1.2rem !important; margin-top: 1.8rem !important; }
.markdown-content h3 { font-size: 1rem !important; margin-top: 1.2rem !important; }
.markdown-content p { line-height: 1.9; color: #C8C6C3; }
.markdown-content ul, .markdown-content ol { padding-left: 1.5rem; margin-bottom: 1rem; }
.markdown-content li { line-height: 1.8; color: #C8C6C3; margin-bottom: 0.3rem; }
.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.85rem;
}
.markdown-content th {
  background: #141417;
  color: #F0B90B;
  padding: 0.6rem 0.8rem;
  text-align: left;
  font-weight: 400;
  border: 1px solid #1A1A1D;
}
.markdown-content td {
  padding: 0.5rem 0.8rem;
  border: 1px solid #1A1A1D;
  color: #C8C6C3;
}
.markdown-content code {
  background: #141417;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  font-size: 0.85em;
  color: #F0B90B;
}
.markdown-content pre {
  background: #0D0D10;
  border: 1px solid #151518;
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
}
.markdown-content pre code {
  background: none;
  padding: 0;
  color: #E8E6E3;
}
.markdown-content blockquote {
  border-left: 3px solid #F0B90B44;
  padding: 0.5rem 1rem;
  margin: 1rem 0;
  background: #0D0D10;
  border-radius: 0 6px 6px 0;
}
.markdown-content strong { color: #F5F0E0; }
.markdown-content hr { border-color: #1A1A1D; margin: 2rem 0; }
</style>
