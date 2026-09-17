<script>
  import { onMount } from "svelte";

  export let onNavigate;

  let token = localStorage.getItem("admin_token") || "";
  let passwordInput = "";
  let loginError = null;

  let messages = [];
  let stats = { pending: 0, approved: 0, rejected: 0, total: 0, print_selected: 0 };
  let activeTab = "pending"; // 'pending', 'approved', 'print_selected', 'rejected', 'all', 'qrcode', 'future'
  let loading = false;
  let actionMessage = null;

  // Edit modal state
  let editingMessage = null;
  let editForm = {
    author_name: "",
    pet_name: "",
    pet_species: "",
    years_known: "",
    message: "",
  };

  let submitSlug = "souvenir-v7k9x4p";
  let customSubmitUrl =
    typeof localStorage !== "undefined"
      ? localStorage.getItem("admin_custom_submit_url") || ""
      : "";

  function saveCustomSubmitUrl() {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem("admin_custom_submit_url", customSubmitUrl);
    }
  }

  $: submitUrl = customSubmitUrl.trim()
    ? customSubmitUrl.trim().endsWith(`/${submitSlug}`) || customSubmitUrl.trim().endsWith(`#/${submitSlug}`)
      ? customSubmitUrl.trim()
      : `${customSubmitUrl.trim().replace(/\/+$/, "")}/${submitSlug}`
    : typeof window !== "undefined"
      ? `${window.location.origin}/${submitSlug}`
      : `https://participer.mondomaine.fr/${submitSlug}`;

  $: qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(submitUrl)}`;

  onMount(() => {
    if (token) {
      fetchAdminMessages();
    }
  });

  async function handleLogin() {
    loginError = null;
    try {
      const res = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: passwordInput }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Mot de passe incorrect");

      token = data.token;
      localStorage.setItem("admin_token", token);
      passwordInput = "";
      fetchAdminMessages();
    } catch (err) {
      loginError = err.message;
    }
  }

  function handleLogout() {
    token = "";
    localStorage.removeItem("admin_token");
  }

  async function fetchAdminMessages() {
    loading = true;
    try {
      fetch("/api/admin/config", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((r) => r.json())
        .then((d) => {
          if (d && d.client_slug) submitSlug = d.client_slug;
        })
        .catch(() => {});

      const res = await fetch("/api/admin/messages", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 401 || res.status === 403) {
        handleLogout();
        return;
      }
      const data = await res.json();
      messages = data.messages || [];
      stats = data.stats || { pending: 0, approved: 0, rejected: 0, total: 0, print_selected: 0 };
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function setStatus(msgId, newStatus) {
    try {
      const res = await fetch(`/api/admin/messages/${msgId}/status`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });
      if (!res.ok) throw new Error("Erreur de mise à jour");
      actionMessage = `Message mis à jour avec le statut: ${newStatus}`;
      setTimeout(() => (actionMessage = null), 3000);
      fetchAdminMessages();
    } catch (err) {
      alert(err.message);
    }
  }

  async function togglePrintSelection(msg) {
    const newVal = !Boolean(msg.include_in_print ?? 1);
    // Optimistic local update
    msg.include_in_print = newVal ? 1 : 0;
    messages = [...messages];
    try {
      const res = await fetch(`/api/admin/messages/${msg.id}/print`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ include_in_print: newVal }),
      });
      if (!res.ok) throw new Error("Erreur lors de la modification de la sélection PDF");
      actionMessage = newVal
        ? `« ${msg.pet_name} » (${msg.author_name}) a été inclus dans le Livre PDF.`
        : `« ${msg.pet_name} » (${msg.author_name}) a été retiré du Livre PDF.`;
      setTimeout(() => (actionMessage = null), 3000);
      fetchAdminMessages();
    } catch (err) {
      alert(err.message);
      fetchAdminMessages();
    }
  }

  async function setBulkPrintSelection(include_in_print) {
    const label = include_in_print ? "inclure tous les messages approuvés" : "retirer tous les messages";
    if (!confirm(`Voulez-vous vraiment ${label} du Livre PDF ?`)) return;
    try {
      const res = await fetch(`/api/admin/messages/print/bulk`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          include_in_print: include_in_print,
          status: "approved",
        }),
      });
      if (!res.ok) throw new Error("Erreur lors de la mise à jour globale");
      actionMessage = include_in_print
        ? `Tous les messages approuvés ont été inclus dans le Livre PDF.`
        : `Tous les messages ont été retirés du Livre PDF.`;
      setTimeout(() => (actionMessage = null), 3000);
      fetchAdminMessages();
    } catch (err) {
      alert(err.message);
    }
  }

  async function handleDelete(msgId) {
    if (
      !confirm(
        "Voulez-vous vraiment supprimer définitivement ce message et sa photo ?",
      )
    )
      return;
    try {
      const res = await fetch(`/api/admin/messages/${msgId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Erreur lors de la suppression");
      fetchAdminMessages();
    } catch (err) {
      alert(err.message);
    }
  }

  function openEditModal(msg) {
    editingMessage = msg;
    editForm = {
      author_name: msg.author_name,
      pet_name: msg.pet_name,
      pet_species: msg.pet_species,
      years_known: msg.years_known || "",
      message: msg.message,
    };
  }

  function closeEditModal() {
    editingMessage = null;
  }

  async function saveEdit() {
    try {
      const res = await fetch(`/api/admin/messages/${editingMessage.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(editForm),
      });
      if (!res.ok) throw new Error("Erreur lors de l'enregistrement");
      closeEditModal();
      fetchAdminMessages();
    } catch (err) {
      alert(err.message);
    }
  }

  $: displayedMessages = messages.filter((m) => {
    if (activeTab === "all") return true;
    if (activeTab === "print_selected") {
      return (m.include_in_print ?? 1) === 1 && m.status === "approved";
    }
    return m.status === activeTab;
  });

  function printQrPoster() {
    window.print();
  }
</script>

<div class="admin-container">
  {#if !token}
    <!-- Login Screen -->
    <div class="login-wrapper">
      <div class="login-card">
        <div class="login-header">
          <span class="lock-icon">🔒</span>
          <h2>Espace Modération</h2>
          <p>Livre d'or du Dr Béatrice</p>
        </div>

        {#if loginError}
          <div class="login-error">⚠️ {loginError}</div>
        {/if}

        <form on:submit|preventDefault={handleLogin}>
          <div class="form-group">
            <label for="pwd">Mot de passe de la clinique</label>
            <input
              id="pwd"
              type="password"
              placeholder="Entrez le mot de passe..."
              bind:value={passwordInput}
              required
            />
          </div>
          <button type="submit" class="btn btn-primary btn-full">
            Se connecter
          </button>
        </form>
      </div>
    </div>
  {:else}
    <!-- Admin Dashboard -->
    <div class="dashboard-header no-print">
      <div>
        <h1>Modération & Gestion</h1>
        <p class="dash-subtitle">
          Espace sécurisé de gestion, diffusion et préparation des souvenirs.
        </p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary btn-projection" on:click={() => onNavigate("diaporama")}>
          <span>🎬</span> Projection Pot de départ
        </button>
        <button class="btn btn-secondary" on:click={() => onNavigate("print")}>
          <span>🖨️</span> Version Imprimable
        </button>
        <button class="btn btn-secondary" on:click={() => onNavigate("home")}>
          <span>📖</span> Voir le Livre d'Or
        </button>
        <button class="btn btn-secondary" on:click={handleLogout}>
          <span>🚪</span> Déconnexion
        </button>
      </div>
    </div>

    {#if actionMessage}
      <div class="toast-message no-print">✅ {actionMessage}</div>
    {/if}

    <!-- Tabs navigation -->
    <div class="admin-tabs no-print">
      <button
        class="tab-btn"
        class:active={activeTab === "pending"}
        on:click={() => (activeTab = "pending")}
      >
        <span>⏳ À Valider</span>
        {#if stats.pending > 0}
          <span class="tab-badge badge-pending">{stats.pending}</span>
        {/if}
      </button>

      <button
        class="tab-btn"
        class:active={activeTab === "approved"}
        on:click={() => (activeTab = "approved")}
      >
        <span>✅ Approuvés</span>
        <span class="tab-badge badge-approved">{stats.approved}</span>
      </button>

      <button
        class="tab-btn tab-btn-print"
        class:active={activeTab === "print_selected"}
        on:click={() => (activeTab = "print_selected")}
      >
        <span>📖 Sélection Livre PDF</span>
        <span class="tab-badge badge-print">{stats.print_selected ?? stats.approved}</span>
      </button>

      <button
        class="tab-btn"
        class:active={activeTab === "rejected"}
        on:click={() => (activeTab = "rejected")}
      >
        <span>🚫 Masqués</span>
        <span class="tab-badge badge-rejected">{stats.rejected}</span>
      </button>

      <button
        class="tab-btn"
        class:active={activeTab === "all"}
        on:click={() => (activeTab = "all")}
      >
        <span>📋 Tous ({stats.total})</span>
      </button>

      <button
        class="tab-btn"
        class:active={activeTab === "qrcode"}
        on:click={() => (activeTab = "qrcode")}
      >
        <span>📱 Affichette QR Code</span>
      </button>

      <button
        class="tab-btn"
        class:active={activeTab === "future"}
        on:click={() => (activeTab = "future")}
      >
        <span>🚀 Fonctionnalités à venir</span>
      </button>
    </div>

    {#if activeTab === "future"}
      <!-- Future Features Tab -->
      <div class="future-features-wrapper no-print">
        <div class="future-header">
          <h2>🚀 Fonctionnalités prévues (en cours de développement)</h2>
          <p class="future-subtitle">
            Ces outils seront activés prochainement pour enrichir l'archivage et l'expérience du départ de Béatrice.
          </p>
        </div>

        <div class="future-grid">
          <div class="future-card">
            <div class="future-icon">📚</div>
            <div class="future-content">
              <div class="future-badge">Bientôt disponible</div>
              <h3>Export Livre Relié & PDF Haute Définition</h3>
              <p>
                Génération automatique d'un fichier PDF prêt à l'impression avec marges de reliure (bleed 3mm), numérotation de pages et couverture rigide.
              </p>
            </div>
          </div>

          <div class="future-card">
            <div class="future-icon">💾</div>
            <div class="future-content">
              <div class="future-badge">Bientôt disponible</div>
              <h3>Archive Complète ZIP (Photos & Vidéos)</h3>
              <p>
                Téléchargement en un clic de l'intégralité des médias bruts (photos HD, vidéos de l'équipe et des clients) classés par date et par auteur.
              </p>
            </div>
          </div>

          <div class="future-card">
            <div class="future-icon">📊</div>
            <div class="future-content">
              <div class="future-badge">Bientôt disponible</div>
              <h3>Statistiques & Mémorial Interactif</h3>
              <p>
                Compteur de visites, nuage de mots-clés d'affection les plus récurrents et frise chronologique des années passées à la clinique.
              </p>
            </div>
          </div>

          <div class="future-card">
            <div class="future-icon">✉️</div>
            <div class="future-content">
              <div class="future-badge">Bientôt disponible</div>
              <h3>Lien de Remerciement Global</h3>
              <p>
                Possibilité d'envoyer une photo ou un mot de remerciement de Béatrice à tous les participants ayant laissé leurs coordonnées.
              </p>
            </div>
          </div>
        </div>
      </div>
    {:else if activeTab === "qrcode"}
      <div class="poster-preview-wrapper">
        <div class="poster-actions no-print">
          <div class="url-config-box">
            <label for="submit-url-input"
              ><strong>🔗 URL du sous-domaine / espace de dépôt client :</strong
              ></label
            >
            <div class="url-input-row">
              <input
                id="submit-url-input"
                type="text"
                bind:value={customSubmitUrl}
                on:input={saveCustomSubmitUrl}
                placeholder="Ex: https://participer.mondomaine.fr (ou http://IP_NAS:9084)"
                class="form-input"
              />
              {#if customSubmitUrl}
                <button
                  class="btn btn-secondary btn-sm"
                  on:click={() => {
                    customSubmitUrl = "";
                    saveCustomSubmitUrl();
                  }}
                >
                  Réinitialiser
                </button>
              {/if}
            </div>
            <small class="text-muted"
              >Le QR Code et le lien sur l'affiche s'ajustent automatiquement en
              temps réel.</small
            >
          </div>
          <button class="btn btn-primary" on:click={printQrPoster}>
            <span>🖨️</span> Imprimer l'Affichette A4
          </button>
        </div>

        <div class="printable-poster">
          <div class="poster-border">
            <div class="poster-top-badge">🐾</div>
            <h1 class="poster-title">Le Dr Béatrice prend sa retraite !</h1>
            <p class="poster-lead">
              Après toutes ces années passées à prendre soin de vos fidèles
              compagnons, laissez-lui un message, une anecdote ou une photo
              souvenir dans son livre d'or.
            </p>

            <div class="poster-qr-section">
              <img
                src={qrCodeUrl}
                alt="QR Code Livre d'or Dr Béatrice"
                class="poster-qr-img"
              />
              <div class="poster-scan-text">
                <strong>Scannez avec votre téléphone</strong>
                <span>pour déposer votre mot doux</span>
              </div>
            </div>

            <div class="poster-url-hint">
              Ou rendez-vous directement sur :<br />
              <code>{submitUrl}</code>
            </div>

            <div class="poster-footer">
              ❤️ Merci pour votre confiance et votre fidélité !
            </div>
          </div>
        </div>
      </div>
    {:else}
      <!-- Messages List -->
      <div class="admin-list-wrapper no-print">
        <!-- PDF Book Selection Banner -->
        <div class="print-selection-banner">
          <div class="print-banner-info">
            <span class="banner-icon">📖</span>
            <div>
              <div class="banner-title">Sélection pour l'Album Imprimable & PDF HD</div>
              <div class="banner-subtitle">
                <strong>{stats.print_selected ?? stats.approved}</strong> message{(stats.print_selected ?? stats.approved) > 1 ? 's' : ''} sélectionné{(stats.print_selected ?? stats.approved) > 1 ? 's' : ''} sur <strong>{stats.approved}</strong> en ligne pour composer le livre souvenir.
              </div>
            </div>
          </div>
          <div class="print-banner-actions">
            <button class="btn btn-sm btn-banner-action" on:click={() => setBulkPrintSelection(true)}>
              ✅ Tout inclure
            </button>
            <button class="btn btn-sm btn-banner-action" on:click={() => setBulkPrintSelection(false)}>
              ❌ Tout désélectionner
            </button>
            <button class="btn btn-sm btn-banner-primary" on:click={() => onNavigate("print")}>
              🖨️ Prévisualiser le PDF
            </button>
          </div>
        </div>

        {#if loading}
          <div class="admin-state">Chargement des messages...</div>
        {:else if displayedMessages.length === 0}
          <div class="admin-state empty">
            <p>
              {#if activeTab === "print_selected"}
                Aucun message n'est actuellement sélectionné pour le Livre PDF.<br />
                <button class="btn btn-sm btn-primary" style="margin-top: 1rem;" on:click={() => (activeTab = "approved")}>
                  Voir les messages approuvés pour en ajouter
                </button>
              {:else}
                Aucun message dans cette section ({activeTab}).
              {/if}
            </p>
          </div>
        {:else}
          <div class="admin-table">
            {#each displayedMessages as msg (msg.id)}
              <div class="admin-card status-{msg.status}">
                <div class="admin-card-header">
                  <div class="author-title">
                    <strong>{msg.author_name}</strong> pour
                    <strong>{msg.pet_name}</strong>
                    <span
                      class="badge-species badge-{msg.pet_species.toLowerCase()}"
                      >{msg.pet_species}</span
                    >
                    {#if msg.years_known}
                      <span class="meta-sub">({msg.years_known})</span>
                    {/if}
                  </div>

                  <div class="header-pills">
                    <!-- PDF Book Inclusion Pill -->
                    <button
                      type="button"
                      class="print-toggle-pill {(msg.include_in_print ?? 1) === 1 ? 'included' : 'excluded'}"
                      on:click={() => togglePrintSelection(msg)}
                      title={(msg.include_in_print ?? 1) === 1 ? "Cliquer pour retirer du Livre PDF" : "Cliquer pour inclure dans le Livre PDF"}
                    >
                      {#if (msg.include_in_print ?? 1) === 1}
                        <span class="pill-icon">📖</span>
                        <span class="pill-text">Dans le Livre PDF</span>
                        <span class="check-mark">✓</span>
                      {:else}
                        <span class="pill-icon">📖</span>
                        <span class="pill-text">Hors Livre PDF</span>
                        <span class="plus-mark">+</span>
                      {/if}
                    </button>

                    <div class="status-pill status-{msg.status}">
                      {msg.status === "pending"
                        ? "⏳ En attente"
                        : msg.status === "approved"
                          ? "✅ En ligne"
                          : "🚫 Masqué"}
                    </div>
                  </div>
                </div>

                <div class="admin-card-body">
                  {#if msg.media_path}
                    <div class="admin-thumb">
                      {#if msg.media_type === "video"}
                        <video
                          src={msg.media_path}
                          controls
                          class="thumb-media"
                        >
                          <track kind="captions" />
                        </video>
                      {:else}
                        <a
                          href={msg.media_path}
                          target="_blank"
                          title="Voir l'image originale HD"
                        >
                          <img
                            src={msg.media_path}
                            alt="Miniature"
                            class="thumb-media"
                          />
                        </a>
                      {/if}
                    </div>
                  {/if}

                  <p class="admin-message-text">« {msg.message} »</p>
                </div>

                <div class="admin-card-actions">
                  <div class="btn-group-status">
                    {#if msg.status !== "approved"}
                      <button
                        class="btn-action btn-approve"
                        on:click={() => setStatus(msg.id, "approved")}
                      >
                        ✅ Approuver & Publier
                      </button>
                    {/if}
                    {#if msg.status !== "rejected"}
                      <button
                        class="btn-action btn-reject"
                        on:click={() => setStatus(msg.id, "rejected")}
                      >
                        🚫 Masquer
                      </button>
                    {/if}
                    {#if msg.status !== "pending"}
                      <button
                        class="btn-action btn-pending-action"
                        on:click={() => setStatus(msg.id, "pending")}
                      >
                        ⏳ Remettre en attente
                      </button>
                    {/if}
                  </div>

                  <div class="btn-group-misc">
                    <button
                      class="btn-action btn-print-action {(msg.include_in_print ?? 1) === 1 ? 'is-included' : 'is-excluded'}"
                      on:click={() => togglePrintSelection(msg)}
                      title={(msg.include_in_print ?? 1) === 1 ? "Retirer de l'album PDF imprimable" : "Ajouter à l'album PDF imprimable"}
                    >
                      {#if (msg.include_in_print ?? 1) === 1}
                        📖 Dans le PDF ✓
                      {:else}
                        📖 + Ajouter au PDF
                      {/if}
                    </button>
                    <button
                      class="btn-action btn-edit"
                      on:click={() => openEditModal(msg)}
                    >
                      ✏️ Modifier texte
                    </button>
                    <button
                      class="btn-action btn-delete"
                      on:click={() => handleDelete(msg.id)}
                    >
                      🗑️ Supprimer
                    </button>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  {/if}
</div>

<!-- Edit Modal -->
{#if editingMessage}
  <div
    class="modal-backdrop"
    on:click={(e) => e.target === e.currentTarget && closeEditModal()}
    on:keydown={(e) => e.key === "Escape" && closeEditModal()}
    role="presentation"
  >
    <div class="modal-card" role="dialog" aria-modal="true" tabindex="-1">
      <h3>Modifier le message #{editingMessage.id}</h3>

      <div class="form-group">
        <label for="edit-author">Nom de l'auteur / famille</label>
        <input id="edit-author" type="text" bind:value={editForm.author_name} />
      </div>

      <div class="form-group">
        <label for="edit-pet">Nom de l'animal</label>
        <input id="edit-pet" type="text" bind:value={editForm.pet_name} />
      </div>

      <div class="form-group">
        <label for="edit-species">Espèce</label>
        <input
          id="edit-species"
          type="text"
          bind:value={editForm.pet_species}
        />
      </div>

      <div class="form-group">
        <label for="edit-years">Années de suivi</label>
        <input id="edit-years" type="text" bind:value={editForm.years_known} />
      </div>

      <div class="form-group">
        <label for="edit-msg">Message</label>
        <textarea id="edit-msg" rows="5" bind:value={editForm.message}
        ></textarea>
      </div>

      <div class="modal-actions">
        <button class="btn btn-secondary" on:click={closeEditModal}
          >Annuler</button
        >
        <button class="btn btn-primary" on:click={saveEdit}
          >Enregistrer les modifications</button
        >
      </div>
    </div>
  </div>
{/if}

<style>
  .admin-container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem;
  }

  .login-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 50vh;
  }

  .login-card {
    background: #ffffff;
    max-width: 440px;
    width: 100%;
    padding: 2.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-lg);
  }

  .login-header {
    text-align: center;
    margin-bottom: 1.8rem;
  }

  .lock-icon {
    font-size: 2.5rem;
  }

  .login-header h2 {
    color: var(--primary);
    margin-top: 0.5rem;
  }

  .login-header p {
    color: var(--text-muted);
    font-size: 0.95rem;
  }

  .login-error {
    background-color: #fef2f2;
    color: #b91c1c;
    padding: 0.75rem;
    border-radius: var(--radius-sm);
    margin-bottom: 1rem;
    font-size: 0.9rem;
    border: 1px solid #fecaca;
  }

  .btn-full {
    width: 100%;
    margin-top: 1.2rem;
  }

  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .dashboard-header h1 {
    color: var(--primary);
    font-size: 2.2rem;
  }

  .dash-subtitle {
    color: var(--text-muted);
  }

  .header-actions {
    display: flex;
    gap: 0.8rem;
  }

  .toast-message {
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
    padding: 0.8rem 1.2rem;
    border-radius: var(--radius-sm);
    margin-bottom: 1.5rem;
    font-weight: 600;
  }

  .admin-tabs {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 0.8rem;
  }

  .tab-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #ffffff;
    border: 1px solid var(--border-subtle);
    padding: 0.6rem 1.2rem;
    border-radius: var(--radius-full);
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .tab-btn:hover {
    background: var(--bg-card-subtle);
  }

  .tab-btn.active {
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
  }

  .tab-badge {
    padding: 0.15rem 0.5rem;
    border-radius: var(--radius-full);
    font-size: 0.75rem;
  }

  .badge-pending {
    background: #fed7aa;
    color: #9a3412;
  }
  .tab-btn.active .badge-pending {
    background: #ffffff;
    color: #9a3412;
  }

  .badge-approved {
    background: #d1fae5;
    color: #065f46;
  }
  .badge-rejected {
    background: #fee2e2;
    color: #991b1b;
  }

  .badge-print {
    background: #fef3c7;
    color: #92400e;
  }
  .tab-btn.active .badge-print {
    background: #ffffff;
    color: #92400e;
  }

  /* PDF Selection Banner */
  .print-selection-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border: 1px solid #fde68a;
    border-radius: var(--radius-md);
    padding: 1rem 1.4rem;
    margin-bottom: 1.5rem;
    gap: 1.2rem;
    flex-wrap: wrap;
    box-shadow: var(--shadow-sm);
  }

  .print-banner-info {
    display: flex;
    align-items: center;
    gap: 0.9rem;
  }

  .banner-icon {
    font-size: 1.8rem;
  }

  .banner-title {
    font-weight: 700;
    color: #92400e;
    font-size: 1rem;
    margin-bottom: 0.2rem;
  }

  .banner-subtitle {
    font-size: 0.88rem;
    color: #78350f;
  }

  .print-banner-actions {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    flex-wrap: wrap;
  }

  .btn-banner-action {
    background: #ffffff;
    border: 1px solid #d97706;
    color: #92400e;
    font-weight: 600;
    padding: 0.35rem 0.75rem;
    border-radius: var(--radius-full);
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .btn-banner-action:hover {
    background: #fef3c7;
  }

  .btn-banner-primary {
    background: #d97706;
    border: 1px solid #b45309;
    color: #ffffff;
    font-weight: 700;
    padding: 0.35rem 0.9rem;
    border-radius: var(--radius-full);
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .btn-banner-primary:hover {
    background: #b45309;
  }

  .header-pills {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    flex-wrap: wrap;
  }

  .print-toggle-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    border-radius: var(--radius-full);
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 700;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s ease;
  }

  .print-toggle-pill.included {
    background: #fef3c7;
    color: #92400e;
    border-color: #fcd34d;
  }
  .print-toggle-pill.included:hover {
    background: #fde68a;
  }

  .print-toggle-pill.excluded {
    background: #f3f4f6;
    color: #6b7280;
    border-color: #e5e7eb;
  }
  .print-toggle-pill.excluded:hover {
    background: #e5e7eb;
    color: #374151;
  }

  .btn-print-action {
    border-radius: var(--radius-sm);
  }
  .btn-print-action.is-included {
    background: #fef3c7;
    color: #92400e;
    border-color: #fcd34d;
  }
  .btn-print-action.is-included:hover {
    background: #fde68a;
  }
  .btn-print-action.is-excluded {
    background: #f9fafb;
    color: #6b7280;
    border: 1px dashed #d1d5db;
  }
  .btn-print-action.is-excluded:hover {
    background: #f3f4f6;
    color: #111827;
  }

  .admin-table {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
  }

  .admin-card {
    background: #ffffff;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-subtle);
    padding: 1.4rem;
    box-shadow: var(--shadow-sm);
  }

  .admin-card.status-pending {
    border-left: 5px solid #f97316;
  }
  .admin-card.status-approved {
    border-left: 5px solid #10b981;
  }
  .admin-card.status-rejected {
    border-left: 5px solid #ef4444;
    opacity: 0.75;
  }

  .admin-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .author-title {
    font-size: 1.05rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .meta-sub {
    color: var(--text-subtle);
    font-size: 0.85rem;
  }

  .status-pill {
    font-size: 0.8rem;
    font-weight: 700;
    padding: 0.25rem 0.7rem;
    border-radius: var(--radius-full);
  }
  .status-pill.status-pending {
    background: #ffedd5;
    color: #9a3412;
  }
  .status-pill.status-approved {
    background: #d1fae5;
    color: #065f46;
  }
  .status-pill.status-rejected {
    background: #fee2e2;
    color: #991b1b;
  }

  .admin-card-body {
    display: flex;
    gap: 1.2rem;
    margin-bottom: 1.2rem;
  }

  .admin-thumb {
    width: 100px;
    height: 100px;
    flex-shrink: 0;
    border-radius: var(--radius-sm);
    overflow: hidden;
    background: #000;
  }

  .thumb-media {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .admin-message-text {
    font-style: italic;
    font-size: 0.95rem;
    line-height: 1.5;
    color: var(--text-main);
    flex: 1;
  }

  .admin-card-actions {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.8rem;
    border-top: 1px solid var(--border-subtle);
    padding-top: 1rem;
  }

  .btn-group-status,
  .btn-group-misc {
    display: flex;
    gap: 0.5rem;
  }

  .btn-action {
    padding: 0.4rem 0.8rem;
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid var(--border-subtle);
    background: var(--bg-main);
  }

  .btn-approve {
    background: #10b981;
    color: #ffffff;
    border-color: #10b981;
  }
  .btn-approve:hover {
    background: #059669;
  }

  .btn-reject {
    background: #ef4444;
    color: #ffffff;
    border-color: #ef4444;
  }
  .btn-reject:hover {
    background: #dc2626;
  }

  .btn-pending-action:hover {
    background: #fed7aa;
  }

  .btn-edit:hover {
    background: #e0e7ff;
    border-color: #6366f1;
  }

  .btn-delete {
    color: #dc2626;
  }
  .btn-delete:hover {
    background: #fee2e2;
  }

  .admin-state {
    text-align: center;
    padding: 3rem;
    background: #ffffff;
    border-radius: var(--radius-md);
    color: var(--text-muted);
  }

  /* Printable Poster */
  .poster-preview-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  .poster-actions {
    text-align: center;
  }

  .printable-poster {
    width: 100%;
    max-width: 600px;
    background: #ffffff;
    padding: 2.5rem;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border-subtle);
  }

  .poster-border {
    border: 4px double var(--primary);
    padding: 2rem;
    text-align: center;
    border-radius: var(--radius-sm);
  }

  .poster-top-badge {
    display: inline-block;
    background: var(--primary-subtle);
    color: var(--primary);
    font-weight: 700;
    font-size: 0.9rem;
    padding: 0.3rem 0.9rem;
    border-radius: var(--radius-full);
    margin-bottom: 1rem;
  }

  .poster-title {
    font-size: 2.2rem;
    color: var(--primary);
    margin-bottom: 1rem;
    line-height: 1.2;
  }

  .poster-lead {
    font-size: 1.05rem;
    color: var(--text-main);
    line-height: 1.5;
    margin-bottom: 2rem;
  }

  .poster-qr-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.8rem;
  }

  .poster-qr-img {
    width: 220px;
    height: 220px;
    border: 6px solid #ffffff;
    box-shadow: var(--shadow-md);
    border-radius: var(--radius-sm);
  }

  .poster-scan-text {
    display: flex;
    flex-direction: column;
    font-size: 1.1rem;
    color: var(--primary);
  }

  .poster-url-hint {
    background: var(--bg-main);
    padding: 0.8rem;
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
  }

  .poster-footer {
    font-weight: 700;
    color: var(--accent);
    font-size: 1rem;
  }

  /* Modal */
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1500;
    padding: 1rem;
  }

  .modal-card {
    background: #ffffff;
    max-width: 550px;
    width: 100%;
    padding: 2rem;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.8rem;
    margin-top: 1rem;
  }

  .btn-projection {
    background: linear-gradient(135deg, #2d5a43 0%, #3e7b5c 100%);
    color: #ffffff;
    box-shadow: 0 2px 6px rgba(45, 90, 67, 0.2);
  }

  .btn-projection:hover {
    background: linear-gradient(135deg, #3e7b5c 0%, #2d5a43 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(45, 90, 67, 0.3);
  }

  /* Future Features Styles */
  .future-features-wrapper {
    background: #ffffff;
    border-radius: var(--radius-md);
    padding: 2rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-subtle);
  }

  .future-header {
    margin-bottom: 2rem;
    text-align: center;
  }

  .future-header h2 {
    font-size: 1.5rem;
    color: var(--primary);
    margin-bottom: 0.5rem;
  }

  .future-subtitle {
    color: var(--text-muted);
    font-size: 0.95rem;
  }

  .future-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .future-card {
    display: flex;
    gap: 1.2rem;
    background: var(--bg-main, #fdfbf7);
    border: 1px dashed var(--border-subtle, #ede7df);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    transition: all var(--transition-fast);
  }

  .future-card:hover {
    border-color: var(--primary);
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
  }

  .future-icon {
    font-size: 2.2rem;
    line-height: 1;
  }

  .future-content {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .future-badge {
    align-self: flex-start;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: #eef2ff;
    color: #4f46e5;
    padding: 0.2rem 0.6rem;
    border-radius: var(--radius-full);
  }

  .future-content h3 {
    font-size: 1.05rem;
    color: var(--text-main);
    margin: 0;
  }

  .future-content p {
    font-size: 0.88rem;
    color: var(--text-muted);
    line-height: 1.4;
    margin: 0;
  }

  @media print {
    .printable-poster {
      box-shadow: none;
      border: none;
      max-width: 100%;
      padding: 0;
    }
  }
</style>
