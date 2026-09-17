<script>
  import { onMount } from "svelte";

  export let onNavigate;

  let messages = [];
  let loading = true;
  let layoutMode = "single"; // 'single' (1 par page) ou 'double' (2 par page)

  async function fetchApprovedMessages() {
    loading = true;
    try {
      const res = await fetch("/api/messages");
      if (res.ok) {
        messages = await res.json();
      }
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchApprovedMessages();
  });

  function triggerPrint() {
    window.print();
  }

  function formatDate(isoStr) {
    if (!isoStr) return "";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString("fr-FR", {
        day: "numeric",
        month: "long",
        year: "numeric",
      });
    } catch {
      return "";
    }
  }
</script>

<div class="print-page-wrapper">
  <!-- Print Control Bar (Hidden when printing) -->
  <aside class="print-toolbar no-print">
    <div class="toolbar-content">
      <div class="toolbar-info">
        <h3>📖 Préparation de l'Album Imprimable</h3>
        <p>
          Ce document est mis en page pour une impression haute qualité (300
          DPI) ou pour l'envoyer à un imprimeur.
        </p>
      </div>

      <div class="toolbar-controls">
        <label class="layout-toggle">
          <span>Format par page :</span>
          <select bind:value={layoutMode}>
            <option value="single"
              >1 souvenir par page (Grand format Prestige)</option
            >
            <option value="double"
              >2 souvenirs par page (Format Album Standard)</option
            >
          </select>
        </label>

        <button class="btn btn-primary" on:click={triggerPrint}>
          <span>🖨️</span> Imprimer / Enregistrer en PDF HD
        </button>

        <button class="btn btn-secondary" on:click={() => onNavigate("admin")}>
          <span>⚙️</span> Retour Administration
        </button>
        <button class="btn btn-secondary" on:click={() => onNavigate("home")}>
          <span>📖</span> Voir le Livre d'Or
        </button>
      </div>
    </div>
  </aside>

  <!-- Printable Document -->
  <main class="album-document">
    <!-- Cover Page -->
    <section class="album-page cover-page page-break">
      <div class="cover-inner">
        <div class="cover-badge">🐾 Carnet de Souvenirs & Gratitude</div>
        <h1 class="cover-title">LIVRE D'OR</h1>
        <h2 class="cover-subtitle">Béatrice</h2>
        <div class="cover-divider"></div>
        <p class="cover-text">
          Témoignages, anecdotes et tendres pensées de tes clients et de leurs
          compagnons.<br />
          À l'occasion de ton départ en retraite.
        </p>
        <div class="cover-footer">
          <span>{messages.length} messages d'affection réunis</span>
          <span class="cover-date">Année 2026</span>
        </div>
      </div>
    </section>

    <!-- Message Pages -->
    {#if loading}
      <div class="loading-box no-print">
        Préparation des images haute résolution...
      </div>
    {:else}
      <div class="album-content layout-{layoutMode}">
        {#each messages as msg, i (msg.id)}
          <article
            class="album-item {layoutMode === 'single'
              ? 'page-break'
              : i % 2 === 1
                ? 'page-break'
                : ''}"
          >
            <div class="item-card">
              {#if msg.media_path && msg.media_type !== "video"}
                <div class="item-media-container">
                  <!-- Full resolution image for high quality print -->
                  <img
                    src={msg.media_path}
                    alt={msg.pet_name}
                    class="item-img"
                  />
                </div>
              {/if}

              <div
                class="item-details"
                class:full-width={!msg.media_path || msg.media_type === "video"}
              >
                <div class="item-header">
                  <div>
                    <h3 class="item-pet-name">{msg.pet_name}</h3>
                    <span class="item-species">{msg.pet_species}</span>
                  </div>
                  {#if msg.years_known}
                    <span class="item-years">{msg.years_known}</span>
                  {/if}
                </div>

                <div class="item-quote">
                  « {msg.message} »
                </div>

                <div class="item-footer">
                  <span class="item-author">{msg.author_name}</span>
                  {#if msg.created_at}
                    <span class="item-date">{formatDate(msg.created_at)}</span>
                  {/if}
                </div>
              </div>
            </div>
          </article>
        {/each}
      </div>
    {/if}

    <!-- Back Cover -->
    <section class="album-page back-cover page-break">
      <div class="back-inner">
        <span class="back-icon">🐾</span>
        <h2>Merci pour toutes ces belles années de soins</h2>
        <p>Clinique Vetalians</p>
      </div>
    </section>
  </main>
</div>

<style>
  .print-page-wrapper {
    background: #e2e8f0;
    min-height: 100vh;
    padding-bottom: 4rem;
  }

  /* Toolbar */
  .print-toolbar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: #1e293b;
    color: #ffffff;
    padding: 1.2rem 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  }

  .toolbar-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1.5rem;
  }

  .toolbar-info h3 {
    font-size: 1.2rem;
    color: #f8fafc;
  }
  .toolbar-info p {
    font-size: 0.85rem;
    color: #94a3b8;
  }

  .toolbar-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .layout-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
  }
  .layout-toggle select {
    background: #334155;
    color: #ffffff;
    border: 1px solid #475569;
    padding: 0.4rem 0.8rem;
    border-radius: var(--radius-sm);
  }

  /* Album Document Body */
  .album-document {
    max-width: 900px;
    margin: 2rem auto;
    background: #ffffff;
    box-shadow: var(--shadow-lg);
  }

  .album-page {
    min-height: 1100px;
    padding: 4rem 3rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #ffffff;
  }

  /* Cover styling */
  .cover-page {
    background: #fbf9f5;
  }

  .cover-inner {
    border: 6px double var(--primary);
    padding: 5rem 3rem;
    width: 100%;
    height: 100%;
    min-height: 900px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }

  .cover-badge {
    font-weight: 700;
    color: var(--primary);
    letter-spacing: 2px;
    font-size: 0.9rem;
    margin-bottom: 2rem;
    text-transform: uppercase;
  }

  .cover-title {
    font-size: 3.5rem;
    color: var(--primary);
    letter-spacing: 4px;
    margin-bottom: 0.5rem;
  }

  .cover-subtitle {
    font-size: 2.5rem;
    color: var(--accent);
    font-weight: 400;
    font-style: italic;
    margin-bottom: 2rem;
  }

  .cover-divider {
    width: 80px;
    height: 3px;
    background: var(--gold);
    margin: 1.5rem auto 2.5rem;
  }

  .cover-text {
    font-size: 1.2rem;
    color: var(--text-muted);
    max-width: 500px;
    line-height: 1.8;
    margin-bottom: 4rem;
  }

  .cover-footer {
    display: flex;
    justify-content: space-between;
    width: 100%;
    max-width: 500px;
    font-size: 0.9rem;
    color: var(--text-subtle);
    border-top: 1px solid var(--border-subtle);
    padding-top: 1.5rem;
  }

  /* Album Items */
  .album-content {
    padding: 2rem 3rem;
  }

  .album-item {
    margin-bottom: 3rem;
    padding-bottom: 2rem;
  }

  .item-card {
    display: flex;
    gap: 2rem;
    background: #faf8f5;
    border: 1px solid #ede8df;
    border-radius: var(--radius-md);
    padding: 2rem;
  }

  .layout-single .item-card {
    min-height: 750px;
    flex-direction: column;
  }

  .item-media-container {
    flex: 1.2;
    min-height: 280px;
    background: #ffffff;
    border-radius: var(--radius-sm);
    overflow: hidden;
    border: 1px solid var(--border-subtle);
  }

  .layout-single .item-media-container {
    min-height: 400px;
  }

  .item-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .item-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .item-details.full-width {
    flex: 1;
  }

  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 0.8rem;
    margin-bottom: 1.2rem;
  }

  .item-pet-name {
    font-size: 1.6rem;
    color: var(--primary);
  }

  .item-species {
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  .item-years {
    font-size: 0.85rem;
    color: var(--text-subtle);
    font-style: italic;
  }

  .item-quote {
    font-family: var(--font-serif);
    font-size: 1.2rem;
    font-style: italic;
    line-height: 1.7;
    color: var(--text-main);
    margin-bottom: 1.5rem;
  }

  .item-footer {
    display: flex;
    justify-content: space-between;
    border-top: 1px dashed var(--border-subtle);
    padding-top: 0.8rem;
    font-size: 0.95rem;
  }

  .item-author {
    font-weight: 700;
    color: var(--primary);
  }

  .item-date {
    color: var(--text-subtle);
    font-size: 0.8rem;
  }

  /* Back Cover */
  .back-cover {
    background: #fbf9f5;
    text-align: center;
  }

  .back-inner {
    border: 2px dashed var(--border-subtle);
    padding: 4rem;
    border-radius: var(--radius-md);
  }

  .back-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
  }

  .back-inner h2 {
    color: var(--primary);
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
  }

  .back-inner p {
    color: var(--text-muted);
  }

  .loading-box {
    text-align: center;
    padding: 4rem;
    color: var(--text-muted);
  }

  /* Print Styles */
  @media print {
    .print-page-wrapper {
      background: #ffffff !important;
      padding: 0 !important;
    }
    .album-document {
      margin: 0 !important;
      max-width: 100% !important;
      box-shadow: none !important;
    }
    .page-break {
      page-break-after: always !important;
      break-after: page !important;
    }
    .item-card {
      break-inside: avoid;
    }
  }
</style>
