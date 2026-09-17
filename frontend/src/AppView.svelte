<script>
  import { onMount } from 'svelte';
  import HomeView from './lib/HomeView.svelte';
  import AdminView from './lib/AdminView.svelte';
  import PrintView from './lib/PrintView.svelte';

  // Secret unguessable route key for administration
  const ADMIN_SECRET_ROUTE = 'admin-k8x7m2q9v3p4z1y';

  let currentRoute = 'home';
  let homeComponent = null;

  function parseRoute() {
    const rawHash = (window.location.hash || '').split('?')[0];
    const cleanHash = rawHash.replace(/^#+\/?/, '').replace(/\/+$/, '').trim().toLowerCase();
    const rawPath = (window.location.pathname || '').replace(/^\/+|\/+$/g, '').trim().toLowerCase();

    const target = cleanHash || rawPath;

    if (target === ADMIN_SECRET_ROUTE.toLowerCase() || target === 'admin') {
      currentRoute = 'admin';
    } else if (target === 'diaporama' || target === 'projection' || target === 'slideshow') {
      currentRoute = 'diaporama';
    } else if (target === 'imprimer' || target === 'print') {
      currentRoute = 'print';
    } else {
      currentRoute = 'home';
    }

    // Clean hash from URL if present to maintain clean URLs
    if (window.location.hash) {
      const cleanPath = target === 'home' || !target ? '/' : `/${target}`;
      window.history.replaceState({}, '', cleanPath);
    }
  }

  function navigateTo(route) {
    let targetPath = '/';
    if (route === 'diaporama') {
      targetPath = '/diaporama';
    } else if (route === 'print') {
      targetPath = '/imprimer';
    } else if (route === 'admin') {
      targetPath = `/${ADMIN_SECRET_ROUTE}`;
    }

    if (window.location.pathname !== targetPath || window.location.hash) {
      window.history.pushState({}, '', targetPath);
    }
    parseRoute();
  }

  function handleStartSlideshow() {
    if (currentRoute === 'home' && homeComponent && homeComponent.triggerSlideshow) {
      homeComponent.triggerSlideshow();
    } else {
      navigateTo('diaporama');
    }
  }

  onMount(() => {
    parseRoute();
    window.addEventListener('popstate', parseRoute);
    window.addEventListener('hashchange', parseRoute);
    return () => {
      window.removeEventListener('popstate', parseRoute);
      window.removeEventListener('hashchange', parseRoute);
    };
  });
</script>

<div class="app-root">
  <!-- Top Navigation Header (hidden on print) -->
  {#if currentRoute !== 'print'}
    <header class="main-navbar no-print">
      <div class="nav-container">
        <div 
          class="brand" 
          on:click={() => navigateTo('home')} 
          on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && navigateTo('home')} 
          role="button" 
          tabindex="0"
        >
          <span class="brand-icon">🐾</span>
          <div class="brand-text">
            <span class="brand-title">Livre d'Or</span>
            <span class="brand-sub">Béatrice</span>
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
            class="nav-link"
            on:click={() => {
              if (currentRoute !== 'home') navigateTo('home');
              setTimeout(() => {
                if (homeComponent && homeComponent.openTeamModal) homeComponent.openTeamModal();
              }, 100);
            }}
            title="Ajouter des photos de l'équipe et souvenirs du pot de départ"
          >
            📸 Photos de l'Équipe
          </button>
        </nav>
      </div>
    </header>
  {/if}

  <!-- View Router -->
  <main class="view-content">
    {#if currentRoute === 'home'}
      <HomeView bind:this={homeComponent} onNavigate={navigateTo} autoStartSlideshow={false} />
    {:else if currentRoute === 'diaporama'}
      <HomeView bind:this={homeComponent} onNavigate={navigateTo} autoStartSlideshow={true} />
    {:else if currentRoute === 'admin'}
      <AdminView onNavigate={navigateTo} />
    {:else if currentRoute === 'print'}
      <PrintView onNavigate={navigateTo} />
    {/if}
  </main>

  <!-- Footer (hidden on print) -->
  {#if currentRoute !== 'print'}
    <footer class="main-footer no-print">
      <div class="footer-inner">
        <p>Livre d'or commémoratif créé avec amour pour le départ en retraite de Béatrice ✨</p>
      </div>
    </footer>
  {/if}
</div>

<style>
  .app-root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--bg-main, #fdfbf7);
  }

  .main-navbar {
    background: #ffffff;
    border-bottom: 1px solid var(--border-subtle, #ede7df);
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow-sm, 0 2px 8px rgba(44, 62, 80, 0.05));
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
    font-family: var(--font-serif, Georgia, serif);
    font-weight: 700;
    font-size: 1.25rem;
    color: var(--primary, #2d5a43);
    line-height: 1.1;
  }

  .brand-sub {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent, #d48b47);
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
    border-radius: var(--radius-full, 9999px);
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-muted, #7c8a82);
    cursor: pointer;
    transition: all var(--transition-fast, 0.2s ease);
  }

  .nav-link:hover {
    background: var(--bg-main, #fdfbf7);
    color: var(--primary, #2d5a43);
  }

  .nav-link.active {
    background: var(--primary-subtle, #f0f7f3);
    color: var(--primary, #2d5a43);
  }

  .view-content {
    flex: 1;
  }

  .main-footer {
    background: #ffffff;
    border-top: 1px solid var(--border-subtle, #ede7df);
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
    color: var(--text-muted, #7c8a82);
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
