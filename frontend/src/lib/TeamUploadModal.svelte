<script>
  import { createEventDispatcher } from 'svelte';

  export let show = false;

  const dispatch = createEventDispatcher();

  let selectedFiles = [];
  let previews = [];
  let authorName = "L'Équipe";
  let customMessage = "";
  let clinicPassword = typeof sessionStorage !== "undefined" ? sessionStorage.getItem("team_upload_password") || "" : "";
  let websiteUrl = ""; // Anti-bot honeypot
  let isUploading = false;
  let errorMsg = null;
  let successMsg = null;

  function handleFilesSelected(event) {
    const files = Array.from(event.target.files || []);
    addFiles(files);
  }

  function handleDrop(event) {
    event.preventDefault();
    if (event.dataTransfer && event.dataTransfer.files) {
      const files = Array.from(event.dataTransfer.files);
      addFiles(files);
    }
  }

  function addFiles(files) {
    errorMsg = null;
    successMsg = null;
    
    for (const file of files) {
      if (file.size > 100 * 1024 * 1024) {
        errorMsg = `Le fichier ${file.name} est trop volumineux (max 100 Mo).`;
        continue;
      }
      
      const isImg = file.type.startsWith('image/');
      const isVid = file.type.startsWith('video/');
      
      if (isImg || isVid) {
        selectedFiles = [...selectedFiles, file];
        previews = [...previews, {
          name: file.name,
          type: isImg ? 'image' : 'video',
          url: URL.createObjectURL(file)
        }];
      }
    }
  }

  function removeFile(index) {
    selectedFiles = selectedFiles.filter((_, i) => i !== index);
    previews = previews.filter((_, i) => i !== index);
  }

  async function handleUpload() {
    if (selectedFiles.length === 0) {
      errorMsg = "Veuillez sélectionner au moins une photo ou vidéo de l'équipe.";
      return;
    }

    if (!clinicPassword.trim()) {
      errorMsg = "Veuillez entrer le mot de passe de la clinique pour autoriser l'envoi.";
      return;
    }

    isUploading = true;
    errorMsg = null;

    try {
      const formData = new FormData();
      formData.append('password', clinicPassword.trim());
      formData.append('author_name', authorName.trim() || "L'Équipe");
      formData.append('message', customMessage.trim() || "Souvenir d'équipe 📸");
      formData.append('website_url', websiteUrl);

      for (const file of selectedFiles) {
        formData.append('files', file);
      }

      const res = await fetch('/api/team/upload', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Erreur lors de l'envoi des photos.");

      if (typeof sessionStorage !== "undefined") {
        sessionStorage.setItem("team_upload_password", clinicPassword.trim());
      }

      successMsg = `${selectedFiles.length} photo(s) ajoutée(s) avec succès !`;

      setTimeout(() => {
        dispatch('uploaded');
        closeModal();
      }, 1400);
    } catch (err) {
      errorMsg = err.message;
    } finally {
      isUploading = false;
    }
  }

  function closeModal() {
    show = false;
    selectedFiles = [];
    previews = [];
    errorMsg = null;
    successMsg = null;
    dispatch('close');
  }
</script>

{#if show}
  <div class="modal-backdrop" on:click={(e) => e.target === e.currentTarget && closeModal()} on:keydown={(e) => e.key === 'Escape' && closeModal()} role="presentation">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="modal-title" tabindex="-1">
      <div class="modal-header">
        <div class="header-icon">📸</div>
        <div>
          <h3 id="modal-title">Ajouter des photos de l'équipe</h3>
          <p class="header-sub">Souvenirs de clinique & pot de départ pour Béatrice</p>
        </div>
        <button class="btn-close" on:click={closeModal} aria-label="Fermer">✕</button>
      </div>

      {#if successMsg}
        <div class="success-banner">
          <span>✨</span> {successMsg}
        </div>
      {:else}
        {#if errorMsg}
          <div class="error-banner">
            <span>⚠️</span> {errorMsg}
          </div>
        {/if}

        <div class="modal-body">
          <!-- Honeypot -->
          <input type="text" bind:value={websiteUrl} class="honeypot" tabindex="-1" autocomplete="off" />

          <div 
            class="drop-zone"
            on:dragover|preventDefault
            on:drop={handleDrop}
            role="region"
            aria-label="Zone de dépôt de photos"
          >
            <div class="drop-content">
              <span class="drop-icon">🖼️</span>
              <p><strong>Glissez vos photos ou vidéos ici</strong></p>
              <span class="drop-sub">ou cliquez pour choisir plusieurs fichiers d'un coup</span>
              <span class="drop-hint">Photos (JPG, PNG, WEBP, HEIC) ou vidéos (MP4, MOV)</span>
              <input 
                type="file" 
                multiple 
                accept="image/*,video/*" 
                on:change={handleFilesSelected}
                class="file-input-overlay"
              />
            </div>
          </div>

          {#if previews.length > 0}
            <div class="previews-container">
              <span class="previews-count">{previews.length} fichier(s) sélectionné(s) :</span>
              <div class="previews-grid">
                {#each previews as p, i}
                  <div class="preview-item">
                    {#if p.type === 'image'}
                      <img src={p.url} alt={p.name} class="preview-thumb" />
                    {:else}
                      <video src={p.url} class="preview-thumb">
                        <track kind="captions" />
                      </video>
                    {/if}
                    <button class="btn-remove-thumb" on:click={() => removeFile(i)} title="Retirer">✕</button>
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          <!-- Form Details -->
          <div class="form-section">
            <div class="form-row">
              <div class="form-group">
                <label for="team-author">Votre Nom ou Rôle</label>
                <input id="team-author" type="text" placeholder="Ex: L'Équipe, Marie, Dr Thomas..." bind:value={authorName} />
              </div>
              <div class="form-group">
                <label for="team-pwd">🔒 Mot de passe équipe <span class="required">*</span></label>
                <input id="team-pwd" type="password" placeholder="Mot de passe équipe..." bind:value={clinicPassword} required />
              </div>
            </div>

            <div class="form-group">
              <label for="team-msg">Légende / Message d'équipe (Optionnel)</label>
              <input id="team-msg" type="text" placeholder="Ex: Un super souvenir de garde ensemble 🐾" bind:value={customMessage} />
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={closeModal} disabled={isUploading}>
            Annuler
          </button>
          <button class="btn btn-primary" on:click={handleUpload} disabled={isUploading || selectedFiles.length === 0}>
            {#if isUploading}
              <span>⏳</span> Envoi de {selectedFiles.length} photo(s)...
            {:else}
              <span>⬆️</span> Téléverser {selectedFiles.length > 0 ? `(${selectedFiles.length} fichier${selectedFiles.length > 1 ? 's' : ''})` : ''}
            {/if}
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(4px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
  }

  .modal-card {
    background: #ffffff;
    border-radius: var(--radius-lg, 16px);
    max-width: 600px;
    width: 100%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    animation: modalPop 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes modalPop {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }

  .modal-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--border-subtle, #ede7df);
    position: relative;
  }

  .header-icon {
    font-size: 2rem;
    background: var(--primary-subtle, #f0f7f3);
    padding: 0.5rem;
    border-radius: 12px;
  }

  .modal-header h3 {
    margin: 0;
    font-family: var(--font-serif, Georgia, serif);
    color: var(--primary, #2d5a43);
    font-size: 1.25rem;
  }

  .header-sub {
    margin: 0.2rem 0 0;
    font-size: 0.85rem;
    color: var(--text-muted, #7c8a82);
  }

  .btn-close {
    position: absolute;
    right: 1.25rem;
    top: 1.25rem;
    background: transparent;
    border: none;
    font-size: 1.2rem;
    color: var(--text-muted, #7c8a82);
    cursor: pointer;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .btn-close:hover {
    background: #f1f5f9;
    color: #0f172a;
  }

  .modal-body {
    padding: 1.5rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
  }

  .honeypot {
    display: none !important;
  }

  .drop-zone {
    border: 2px dashed var(--primary-light, #3e7b5c);
    background: var(--primary-subtle, #f0f7f3);
    border-radius: 12px;
    padding: 1.8rem 1.2rem;
    text-align: center;
    position: relative;
    cursor: pointer;
    transition: all 0.2s;
  }
  .drop-zone:hover {
    background: #e2efe8;
    border-color: var(--primary, #2d5a43);
  }

  .drop-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
  }

  .drop-icon {
    font-size: 2.2rem;
  }

  .drop-sub {
    font-size: 0.9rem;
    color: var(--primary, #2d5a43);
    font-weight: 500;
  }

  .drop-hint {
    font-size: 0.78rem;
    color: var(--text-muted, #7c8a82);
  }

  .file-input-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
  }

  .previews-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .previews-count {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--primary, #2d5a43);
  }

  .previews-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(75px, 1fr));
    gap: 0.5rem;
    max-height: 180px;
    overflow-y: auto;
    padding: 0.3rem;
    background: var(--bg-main, #fdfbf7);
    border-radius: 8px;
    border: 1px solid var(--border-subtle, #ede7df);
  }

  .preview-item {
    position: relative;
    aspect-ratio: 1;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--border-subtle, #ede7df);
  }

  .preview-thumb {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .btn-remove-thumb {
    position: absolute;
    top: 2px;
    right: 2px;
    background: rgba(0, 0, 0, 0.65);
    color: #ffffff;
    border: none;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    font-size: 0.65rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  .form-section {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
    border-top: 1px solid var(--border-subtle, #ede7df);
    padding-top: 1rem;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.8rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .form-group label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-main, #2c3e50);
  }

  .required {
    color: #dc2626;
  }

  .form-group input {
    padding: 0.65rem 0.85rem;
    border-radius: 6px;
    border: 1px solid var(--border-subtle, #ede7df);
    font-size: 0.9rem;
    outline: none;
    background: #ffffff;
    transition: border-color 0.2s ease;
  }

  .form-group input:focus {
    border-color: var(--primary, #2d5a43);
    box-shadow: 0 0 0 2px rgba(45, 90, 67, 0.15);
  }

  .modal-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border-subtle, #ede7df);
    display: flex;
    justify-content: flex-end;
    gap: 0.8rem;
    background: #fafaf9;
  }

  .error-banner {
    background: #feebc8;
    color: #c05621;
    padding: 0.8rem 1.2rem;
    margin: 1rem 1.5rem 0;
    border-radius: 8px;
    font-size: 0.9rem;
  }

  .success-banner {
    padding: 2.5rem 1.5rem;
    text-align: center;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--primary, #2d5a43);
  }

  @media (max-width: 550px) {
    .form-row {
      grid-template-columns: 1fr;
    }
  }
</style>
