declare module 'relationship.js' {
  interface Options {
    text: string
    sex?: 0 | 1
    reverse?: boolean
    type?: 'default' | 'chain' | 'pair'
  }
  
  function relationship(options: Options): string[]
  function relationship(text: string): string[]
  
  export default relationship
}
