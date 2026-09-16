import { mount } from 'svelte'
import './app.css'
import AppView from './AppView.svelte'

const app = mount(AppView, {
  target: document.getElementById('app'),
})

export default app
