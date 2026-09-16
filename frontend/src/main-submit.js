import { mount } from 'svelte'
import './app.css'
import AppSubmit from './AppSubmit.svelte'

const app = mount(AppSubmit, {
  target: document.getElementById('app'),
})

export default app
