<script>
  import { onMount } from 'svelte';
  import HomeView from './lib/HomeView.svelte';
  import SubmitForm from './lib/SubmitForm.svelte';
  import AdminView from './lib/AdminView.svelte';
  import PrintView from './lib/PrintView.svelte';

  let currentRoute = 'home';
  let tokenParam = 'retraitebs-7x8k2q';

  function parseHash() {
    const hash = window.location.hash.replace(/^#\/?/, '');
    
    if (hash.startsWith('participer')) {
      const parts = hash.split('/');
      tokenParam = parts[1] || 'retraitebs-7x8k2q';
      currentRoute = 'submit';
    } else if (hash === 'admin') {
      currentRoute = 'admin';
    } else if (hash === 'imprimer' || hash === 'print') {
      currentRoute = 'print';
    } else {
      currentRoute = 'home';
    }
  }

  function navigateTo(route, token = 'retraitebs-7x8k2q') {
    if (route === 'home') {
      window.location.hash = '#/';
    } else if (route === 'submit') {
      window.location.hash = `#/participer/${token}`;
    } else if (route === 'admin') {
      window.location.hash = '#/admin';
    } else if (route === 'print') {
      window.location.hash = '#/imprimer';
    }
    parseHash();
  }

  onMount(() => {
    parseHash();
    window.addEventListener('hashchange', parseHash);
    return () => window.removeEventListener('hashchange', parseHash);
  });
</script>

<div class="app-root">
  <!-- Top Navigation Header (hidden on print) -->
  {#if currentRoute !== 'print'}
    <header class="main-navbar no-print">
      <div class="nav-container">
        <div class="brand" on:click={() => navigateTo('home')}>
          <span class="brand-icon">🐾</span>
          <div class="brand-text">
            <span class="brand-title">Livre d'Or</span>
            <span class="brand-sub">Dr Béatrice</span>
          </div>
        </div>

        <nav class="nav-links">
          <button 
            class="nav-link" 
            class:active={currentRoute === 'home'}
            on:click={() => navigateTo('home')}
          >
            📖 Le Livre d'Or
          </button>

          <button 
            class="nav-link btn-nav-cta" 
            class:active={currentRoute === 'submit'}
            on:click={() => navigateTo('submit')}
          >
            ✍️ Déposer un message
          </button>

          <button 
            class="nav-link" 
            class:active={currentRoute === 'admin'}
            on:click={() => navigateTo('admin')}
          >
            🔒 Modération
          </button>
        </nav>
      </div>
    </header>
  {/if}

  <!-- View Router -->
  <div class="view-content">
    {#if currentRoute === 'home'}
      <HomeView onNavigate={navigateTo} />
    {:else if currentRoute === 'submit'}
      <SubmitForm token={tokenParam} onNavigate={navigateTo} />
    {:else if currentRoute === 'admin'}
      <AdminView onNavigate={navigateTo} />
    {:else if currentRoute === 'print'}
      <PrintView onNavigate={navigateTo} />
    {/if}
  </div>

  <!-- Footer (hidden on print) -->
  {#if currentRoute !== 'print'}
    <footer class="main-footer no-print">
      <div class="footer-inner">
        <p>Livre d'or commémoratif créé avec amour pour le départ en retraite du Dr Béatrice ✨</p>
        <div class="footer-links">
          <button on:click={() => navigateTo('home')}>Accueil</button>
          <span>•</span>
          <button on:click={() => navigateTo('submit')}>Déposer un mot</button>
          <span>•</span>
          <button on:click={() => navigateTo('print')}>Format Album Papier</button>
          <span>•</span>
          <button on:click={() => navigateTo('admin')}>Accès Clinique</button>
        </div>
      </div>
    </footer>
  {/if}
</div>

<style>
  .app-root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .main-navbar {
    background: #ffffff;
    border-bottom: 1px solid var(--border-subtle);
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow-sm);
  }

  .nav-container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0.8rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    cursor: pointer;
  }

  .brand-icon {
    font-size: 1.8rem;
  }

  .brand-text {
    display: flex;
    flex-direction: column;
  }

  .brand-title {
    font-family: var(--font-serif);
    font-weight: 700;
    font-size: 1.25rem;
    color: var(--primary);
    line-height: 1.1;
  }

  .brand-sub {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }

  .nav-link {
    background: transparent;
    border: none;
    padding: 0.5rem 0.9rem;
    border-radius: var(--radius-full);
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-muted);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .nav-link:hover {
    background: var(--bg-main);
    color: var(--primary);
  }

  .nav-link.active {
    background: var(--primary-subtle);
    color: var(--primary);
  }

  .btn-nav-cta {
    background: var(--primary);
    color: #ffffff;
  }
  .btn-nav-cta:hover {
    background: var(--primary-light);
    color: #ffffff;
  }
  .btn-nav-cta.active {
    background: var(--primary-light);
    color: #ffffff;
  }

  .view-content {
    flex: 1;
  }

  .main-footer {
    background: #ffffff;
    border-top: 1px solid var(--border-subtle);
    padding: 2rem 1.5rem;
    margin-top: auto;
  }

  .footer-inner {
    max-width: 1200px;
    margin: 0 auto;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    font-size: 0.9rem;
    color: var(--text-muted);
  }

  .footer-links {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.6rem;
  }

  .footer-links button {
    background: none;
    border: none;
    color: var(--primary);
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
  }
  .footer-links button:hover {
    text-decoration: underline;
  }

  @media (max-width: 650px) {
    .brand-sub {
      display: none;
    }
    .nav-link {
      padding: 0.4rem 0.6rem;
      font-size: 0.8rem;
    }
  }
</style>
