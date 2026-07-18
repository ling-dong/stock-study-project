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
      return marked(this.content, { breaks: true, gfm: true })
    }
  },
}
</script>

<style>
.markdown-content h1 { font-size: 1.5rem !important; color: var(--ia-text); margin-top: 0; }
.markdown-content h2 { font-size: 1.2rem !important; margin-top: 1.6rem !important; color: var(--ia-text); border-bottom: 1px solid var(--ia-border); padding-bottom: 0.4rem; }
.markdown-content h3 { font-size: 1.05rem !important; margin-top: 1.2rem !important; color: var(--ia-text); }
.markdown-content p { line-height: 1.85; color: var(--ia-text-secondary); margin-bottom: 0.8rem; }
.markdown-content ul, .markdown-content ol { padding-left: 1.5rem; margin-bottom: 1rem; }
.markdown-content li { line-height: 1.75; color: var(--ia-text-secondary); margin-bottom: 0.3rem; }
.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: var(--ia-font-size-sm);
  border: 1px solid var(--ia-border);
  border-radius: var(--ia-radius-xs);
  overflow: hidden;
}
.markdown-content th {
  background: var(--ia-surface-elevated);
  color: var(--ia-gold);
  padding: 0.6rem 0.8rem;
  text-align: left;
  font-weight: 500;
  border-bottom: 1px solid var(--ia-border);
}
.markdown-content td {
  padding: 0.5rem 0.8rem;
  border-bottom: 1px solid var(--ia-border);
  color: var(--ia-text-secondary);
}
.markdown-content code {
  background: var(--ia-surface-elevated);
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  font-size: 0.85em;
  color: var(--ia-gold);
  font-family: var(--ia-font-mono);
}
.markdown-content pre {
  background: var(--ia-bg);
  border: 1px solid var(--ia-border);
  border-radius: var(--ia-radius-sm);
  padding: 1rem;
  overflow-x: auto;
}
.markdown-content pre code { background: none; padding: 0; color: var(--ia-text); }
.markdown-content blockquote {
  border-left: 3px solid var(--ia-gold);
  padding: 0.5rem 1rem;
  margin: 1rem 0;
  background: var(--ia-surface);
  border-radius: 0 var(--ia-radius-xs) var(--ia-radius-xs) 0;
  color: var(--ia-text-secondary);
}
.markdown-content strong { color: var(--ia-text); }
.markdown-content hr { border-color: var(--ia-border); margin: 2rem 0; }
</style>
