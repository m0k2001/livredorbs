<script>
  import { onMount, onDestroy } from 'svelte';
  import TeamUploadModal from './TeamUploadModal.svelte';

  export let onNavigate = null;
  export let autoStartSlideshow = false;

  let messages = [];
  let loading = true;
  let error = null;
  let activeFilter = 'tous';
  let searchQuery = '';
  let showTeamModal = false;

  // Lightbox & Slideshow state
  let selectedMessage = null;
  let slideshowActive = false;
  let slideshowIndex = 0;
  let slideshowTimer = null;
  let slideshowProgress = 0;
  let progressInterval = null;

  const speciesList = [
    { id: 'tous', label: 'Tous les souvenirs', icon: '🐾' },
    { id: 'équipe', label: 'Équipe & Clinique', icon: '📸' },
    { id: 'chien', label: 'Chiens', icon: '🐶' },
    { id: 'chat', label: 'Chats', icon: '🐱' },
    { id: 'autre', label: 'Autres', icon: '✨' }
  ];

  async function fetchMessages() {
    loading = true;
    error = null;
    try {
      const res = await fetch('/api/messages');
      if (!res.ok) throw new Error("Impossible de charger les messages");
      messages = await res.json();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
      if (autoStartSlideshow && messages.length > 0) {
        startSlideshow();
      }
    }
  }

  export function triggerSlideshow() {
    startSlideshow();
  }

  onMount(() => {
    fetchMessages();
  });

  onDestroy(() => {
    stopSlideshow();
  });

  $: filteredMessages = messages.filter(msg => {
    const matchSpecies = activeFilter === 'tous' || (msg.pet_species && msg.pet_species.toLowerCase() === activeFilter.toLowerCase());
    const query = searchQuery.toLowerCase().trim();
    if (!query) return matchSpecies;
    const matchSearch = (
      (msg.author_name && msg.author_name.toLowerCase().includes(query)) ||
      (msg.pet_name && msg.pet_name.toLowerCase().includes(query)) ||
      (msg.message && msg.message.toLowerCase().includes(query))
    );
    return matchSpecies && matchSearch;
  });

  function openLightbox(msg) {
    selectedMessage = msg;
  }

  function closeLightbox() {
    selectedMessage = null;
  }

  function startSlideshow() {
    if (filteredMessages.length === 0) return;
    slideshowActive = true;
    slideshowIndex = 0;
    runSlideshowStep();
  }

  function stopSlideshow() {
    slideshowActive = false;
    if (slideshowTimer) clearTimeout(slideshowTimer);
    if (progressInterval) clearInterval(progressInterval);
    slideshowProgress = 0;
  }

  function runSlideshowStep() {
    if (slideshowTimer) clearTimeout(slideshowTimer);
    if (progressInterval) clearInterval(progressInterval);
    slideshowProgress = 0;

    const DURATION = 8000;
    const STEP = 50;

    progressInterval = setInterval(() => {
      slideshowProgress += (STEP / DURATION) * 100;
      if (slideshowProgress >= 100) {
        slideshowProgress = 100;
      }
    }, STEP);

    slideshowTimer = setTimeout(() => {
      slideshowIndex = (slideshowIndex + 1) % filteredMessages.length;
      runSlideshowStep();
    }, DURATION);
  }

  function nextSlide() {
    slideshowIndex = (slideshowIndex + 1) % filteredMessages.length;
    runSlideshowStep();
  }

  function prevSlide() {
    slideshowIndex = (slideshowIndex - 1 + filteredMessages.length) % filteredMessages.length;
    runSlideshowStep();
  }

  function getSpeciesIcon(species) {
    if (!species) return '🐾';
    const s = species.toLowerCase();
    if (s.includes('équipe') || s.includes('equipe')) return '👥';
    if (s.includes('chien')) return '🐶';
    if (s.includes('chat')) return '🐱';
    if (s.includes('nac') || s.includes('lapin') || s.includes('rongeur') || s.includes('oiseau')) return '🐰';
    if (s.includes('cheval') || s.includes('équid')) return '🐴';
    return '🐾';
  }

  export function openTeamModal() {
    showTeamModal = true;
  }

  function formatDate(isoStr) {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
    } catch {
      return '';
    }
  }
</script>

<div class="tribute-container">
  <!-- Hero Section -->
  <header class="hero">
    <div class="hero-badge">
      <span class="star-icon">✨</span> Bonne retraite Béatrice !
    </div>
    <h1 class="hero-title">Le Livre d'Or de Béatrice</h1>
    <p class="hero-subtitle">
      Des années de dévouement, de soins attentifs et de bienveillance auprès de nos fidèles compagnons. 
      Retrouvez ici tous les témoignages d'amour et de reconnaissance de vos clients et de l'équipe.
    </p>

    <div class="hero-actions">
      <button class="btn btn-team" on:click={() => showTeamModal = true}>
        <span>📸</span> Ajouter des photos de l'Équipe
      </button>
    </div>

    <!-- Quick stats badge -->
    <div class="stats-ribbon">
      <div class="stat-item">
        <span class="stat-number">{messages.length}</span>
        <span class="stat-label">Messages d'affection reçus</span>
      </div>
    </div>
  </header>

  <!-- Filter & Search Bar -->
  <div class="filter-section">
    <div class="species-filters">
      {#each speciesList as sp}
        <button 
          class="filter-pill" 
          class:active={activeFilter === sp.id}
          on:click={() => activeFilter = sp.id}
        >
          <span>{sp.icon}</span> {sp.label}
        </button>
      {/each}
    </div>

    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input 
        type="text" 
        placeholder="Rechercher un animal, une famille..." 
        bind:value={searchQuery}
      />
      {#if searchQuery}
        <button class="clear-search" on:click={() => searchQuery = ''}>✕</button>
      {/if}
    </div>
  </div>

  <!-- Main Content Cards -->
  <main class="gallery-wrapper">
    {#if loading}
      <div class="state-card">
        <div class="spinner"></div>
        <p>Ouverture du livre de souvenirs...</p>
      </div>
    {:else if error}
      <div class="state-card error">
        <p>⚠️ {error}</p>
        <button class="btn btn-secondary" on:click={fetchMessages}>Réessayer</button>
      </div>
    {:else if filteredMessages.length === 0}
      <div class="state-card empty">
        <div class="empty-icon">📖</div>
        <h3>Aucun message dans cette catégorie pour l'instant</h3>
        <p>Les messages validés par l'équipe apparaîtront ici au fur et à mesure.</p>
      </div>
    {:else}
      <div class="cards-grid">
        {#each filteredMessages as msg (msg.id)}
          <article class="polaroid-card">
            <!-- Media block if exists -->
            {#if msg.media_path}
              <div 
                class="media-frame" 
                on:click={() => openLightbox(msg)}
                on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && openLightbox(msg)}
                role="button"
                tabindex="0"
                aria-label="Agrandir la photo ou vidéo"
              >
                {#if msg.media_type === 'video'}
                  <video 
                    src={msg.media_path} 
                    controls 
                    preload="metadata"
                    class="card-video"
                  >
                    <track kind="captions" />
                  </video>
                {:else}
                  <img 
                    src={msg.media_path} 
                    alt={msg.pet_name || 'Souvenir'} 
                    loading="lazy" 
                    class="card-image"
                  />
                  <div class="zoom-badge">🔍 Voir en grand HD</div>
                {/if}
              </div>
            {/if}

            <!-- Content block -->
            <div class="card-body">
              <div class="pet-header">
                <div class="pet-avatar">
                  {getSpeciesIcon(msg.pet_species)}
                </div>
                <div>
                  <h3 class="pet-name">{msg.pet_name}</h3>
                  <span class="badge-species badge-{msg.pet_species ? msg.pet_species.toLowerCase() : 'autre'}">
                    {msg.pet_species || 'Animal'}
                  </span>
                </div>
              </div>

              {#if msg.years_known}
                <div class="years-pill">
                  <span>⏳</span> {msg.years_known}
                </div>
              {/if}

              <blockquote class="message-quote">
                « {msg.message} »
              </blockquote>

              <footer class="card-footer">
                <div class="author-info">
                  <span class="author-name">{msg.author_name}</span>
                  {#if msg.created_at}
                    <span class="post-date">{formatDate(msg.created_at)}</span>
                  {/if}
                </div>
              </footer>
            </div>
          </article>
        {/each}
      </div>
    {/if}
  </main>
</div>

<!-- HD Lightbox Modal -->
{#if selectedMessage}
  <div 
    class="lightbox-backdrop" 
    on:click={(e) => e.target === e.currentTarget && closeLightbox()}
    on:keydown={(e) => e.key === 'Escape' && closeLightbox()}
    role="presentation"
  >
    <div 
      class="lightbox-content" 
      role="dialog"
      aria-modal="true"
      tabindex="-1"
    >
      <button class="lightbox-close" on:click={closeLightbox}>✕ Fermer</button>
      {#if selectedMessage.media_type === 'video'}
        <video src={selectedMessage.media_path} controls autoplay class="lightbox-media">
          <track kind="captions" />
        </video>
      {:else}
        <img src={selectedMessage.media_path} alt={selectedMessage.pet_name || 'Souvenir'} class="lightbox-media" />
      {/if}
      <div class="lightbox-caption">
        <h4>{selectedMessage.pet_name} — {selectedMessage.author_name}</h4>
        <p>« {selectedMessage.message} »</p>
      </div>
    </div>
  </div>
{/if}

<!-- Slideshow Mode (Full Screen Projection) -->
{#if slideshowActive && filteredMessages.length > 0}
  {@const current = filteredMessages[slideshowIndex]}
  <div class="slideshow-overlay">
    <!-- Progress bar -->
    <div class="slideshow-progress-bar" style="width: {slideshowProgress}%;"></div>

    <!-- Slideshow Top Bar -->
    <div class="slideshow-topbar">
      <div class="slideshow-branding">
        <span>🐾</span> Livre d'Or Béatrice ({slideshowIndex + 1} / {filteredMessages.length})
      </div>
      <div class="slideshow-controls">
        <button class="btn-ctrl" on:click={prevSlide}>◀ Précédent</button>
        <button class="btn-ctrl" on:click={nextSlide}>Suivant ▶</button>
        <button class="btn-ctrl btn-close-slideshow" on:click={stopSlideshow}>✕ Quitter le Diaporama</button>
      </div>
    </div>

    <!-- Slideshow Stage -->
    <div class="slideshow-stage">
      <div class="slide-card">
        {#if current.media_path}
          <div class="slide-media-container">
            {#if current.media_type === 'video'}
              <video src={current.media_path} controls autoplay class="slide-media">
                <track kind="captions" />
              </video>
            {:else}
              <img src={current.media_path} alt={current.pet_name} class="slide-media" />
            {/if}
          </div>
        {/if}

        <div class="slide-content">
          <div class="slide-pet-info">
            <span class="slide-icon">{getSpeciesIcon(current.pet_species)}</span>
            <h2>{current.pet_name}</h2>
            {#if current.years_known}
              <span class="slide-years">({current.years_known})</span>
            {/if}
          </div>

          <div class="slide-quote">
            « {current.message} »
          </div>

          <div class="slide-author">
            — {current.author_name}
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- Team Upload Modal -->
<TeamUploadModal bind:show={showTeamModal} on:uploaded={fetchMessages} />

<style>
  .tribute-container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 2rem 1.5rem 5rem;
  }

  /* Hero */
  .hero {
    text-align: center;
    padding: 3.5rem 1.5rem 2.5rem;
    background: linear-gradient(180deg, rgba(234, 242, 237, 0.7) 0%, rgba(251, 249, 245, 0.2) 100%);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-subtle);
    margin-bottom: 2.5rem;
  }

  .hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #fef3c7;
    color: #92400e;
    padding: 0.4rem 1.1rem;
    border-radius: var(--radius-full);
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 1.2rem;
  }

  .hero-title {
    font-size: 2.8rem;
    color: var(--primary);
    margin-bottom: 1rem;
    line-height: 1.2;
  }

  .hero-subtitle {
    max-width: 680px;
    margin: 0 auto 1.8rem;
    color: var(--text-muted);
    font-size: 1.15rem;
  }

  .hero-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
  }

  .btn-team {
    background: linear-gradient(135deg, #d48b47 0%, #b86e2d 100%);
    color: #ffffff;
    border: none;
    padding: 0.8rem 1.4rem;
    border-radius: var(--radius-full);
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(212, 139, 71, 0.25);
    transition: all var(--transition-normal);
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }
  .btn-team:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(212, 139, 71, 0.35);
  }

  .stats-ribbon {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-top: 1rem;
    border-top: 1px dashed var(--border-subtle);
    padding-top: 1.5rem;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .stat-number {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--primary);
  }

  .stat-label {
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  /* Filters */
  .filter-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin-bottom: 2.5rem;
    background: #ffffff;
    padding: 1rem 1.4rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-sm);
  }

  .species-filters {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
  }

  .filter-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--bg-main);
    border: 1px solid var(--border-subtle);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-full);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .filter-pill:hover {
    background: var(--primary-subtle);
    border-color: var(--primary);
  }

  .filter-pill.active {
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
  }

  .search-box {
    display: flex;
    align-items: center;
    background: var(--bg-main);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-full);
    padding: 0.4rem 1rem;
    min-width: 260px;
  }

  .search-box input {
    border: none;
    background: transparent;
    outline: none;
    padding: 0.3rem 0.5rem;
    width: 100%;
    font-size: 0.9rem;
  }

  .clear-search {
    background: none;
    border: none;
    color: var(--text-subtle);
    cursor: pointer;
    font-size: 0.9rem;
  }

  /* Cards Grid */
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 2rem;
  }

  .polaroid-card {
    background: var(--bg-card);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-md);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  }

  .polaroid-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-hover);
  }

  .media-frame {
    position: relative;
    width: 100%;
    height: 260px;
    background-color: #1a1a1a;
    overflow: hidden;
    cursor: pointer;
  }

  .card-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.4s ease;
  }

  .polaroid-card:hover .card-image {
    transform: scale(1.03);
  }

  .card-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .zoom-badge {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: rgba(0, 0, 0, 0.65);
    color: #ffffff;
    font-size: 0.75rem;
    padding: 0.25rem 0.65rem;
    border-radius: var(--radius-full);
    backdrop-filter: blur(4px);
  }

  .card-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .pet-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.8rem;
  }

  .pet-avatar {
    width: 44px;
    height: 44px;
    background: var(--primary-subtle);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
  }

  .pet-name {
    font-size: 1.3rem;
    color: var(--primary);
    line-height: 1.1;
    margin-bottom: 0.2rem;
  }

  .years-pill {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
  }

  .message-quote {
    font-family: var(--font-serif);
    font-size: 1.05rem;
    font-style: italic;
    color: var(--text-main);
    line-height: 1.6;
    margin-bottom: 1.5rem;
    flex: 1;
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-top: 1px solid var(--border-subtle);
    padding-top: 1rem;
  }

  .author-info {
    display: flex;
    flex-direction: column;
  }

  .author-name {
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--primary);
  }

  .post-date {
    font-size: 0.75rem;
    color: var(--text-subtle);
  }

  .heart-btn {
    background: none;
    border: none;
    font-size: 1.3rem;
    cursor: pointer;
    transition: transform 0.2s ease;
    padding: 0.2rem;
  }
  .heart-btn:hover {
    transform: scale(1.3);
  }

  /* States */
  .state-card {
    text-align: center;
    padding: 4rem 2rem;
    background: #ffffff;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-subtle);
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-subtle);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 1rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  /* Lightbox */
  .lightbox-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.88);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1.5rem;
  }

  .lightbox-content {
    position: relative;
    max-width: 900px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .lightbox-close {
    position: absolute;
    top: -45px;
    right: 0;
    background: #ffffff;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: var(--radius-full);
    font-weight: 700;
    cursor: pointer;
  }

  .lightbox-media {
    max-width: 100%;
    max-height: 75vh;
    object-fit: contain;
    border-radius: var(--radius-md);
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  }

  .lightbox-caption {
    margin-top: 1rem;
    color: #ffffff;
    text-align: center;
  }

  /* Slideshow View */
  .slideshow-overlay {
    position: fixed;
    inset: 0;
    background-color: #1a2421;
    color: #ffffff;
    z-index: 2000;
    display: flex;
    flex-direction: column;
  }

  .slideshow-progress-bar {
    height: 4px;
    background: var(--gold);
    transition: width 0.05s linear;
  }

  .slideshow-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: rgba(0,0,0,0.4);
  }

  .slideshow-branding {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e5ded4;
  }

  .slideshow-controls {
    display: flex;
    gap: 0.8rem;
  }

  .btn-ctrl {
    background: rgba(255, 255, 255, 0.15);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 0.4rem 0.9rem;
    border-radius: var(--radius-full);
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s ease;
  }
  .btn-ctrl:hover {
    background: rgba(255, 255, 255, 0.3);
  }
  .btn-close-slideshow {
    background: var(--accent);
    border-color: var(--accent);
  }

  .slideshow-stage {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }

  .slide-card {
    display: flex;
    background: #ffffff;
    color: var(--text-main);
    border-radius: var(--radius-lg);
    overflow: hidden;
    max-width: 1050px;
    width: 100%;
    min-height: 480px;
    max-height: 80vh;
    box-shadow: 0 25px 60px rgba(0,0,0,0.5);
  }

  .slide-media-container {
    flex: 1.2;
    background: #000000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .slide-media {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .slide-text-container {
    flex: 1;
    padding: 3rem 2.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .slide-text-container.full-width {
    flex: 1;
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
  }

  .slide-pet-info {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    margin-bottom: 0.5rem;
  }

  .slide-icon {
    font-size: 2rem;
  }

  .slide-pet-info h2 {
    font-size: 2.2rem;
    color: var(--primary);
  }

  .slide-species {
    background: var(--primary-subtle);
    color: var(--primary);
    padding: 0.2rem 0.6rem;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    font-weight: 600;
  }

  .slide-years {
    font-size: 0.95rem;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
  }

  .slide-quote {
    font-family: var(--font-serif);
    font-size: 1.45rem;
    font-style: italic;
    line-height: 1.5;
    color: var(--text-main);
    margin-bottom: 2rem;
  }

  .slide-author {
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--primary);
  }

  @media (max-width: 768px) {
    .hero-title {
      font-size: 2rem;
    }
    .cards-grid {
      grid-template-columns: 1fr;
    }
    .slide-card {
      flex-direction: column;
      max-height: 90vh;
      overflow-y: auto;
    }
    .slide-media-container {
      height: 240px;
    }
    .slide-text-container {
      padding: 1.5rem;
    }
  }
</style>
