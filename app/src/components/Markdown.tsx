import ReactMarkdown, { type Options } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'

// Single tildes appear in prose ("~5 minutes") and must not become strikethrough.
const remarkPlugins: Options['remarkPlugins'] = [[remarkGfm, { singleTilde: false }], remarkMath]

export function Markdown({ text, inline = false }: { text: string; inline?: boolean }) {
  return (
    <div className={inline ? 'md md-inline' : 'md'}>
      <ReactMarkdown remarkPlugins={remarkPlugins} rehypePlugins={[rehypeKatex]}>
        {text}
      </ReactMarkdown>
    </div>
  )
}
