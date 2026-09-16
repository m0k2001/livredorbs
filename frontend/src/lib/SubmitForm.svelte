<script>
  import { onMount } from "svelte";
  import confetti from "canvas-confetti";

  export let token = "retraitebs-7x8k2q";
  export let onNavigate = null;
  export let showDiscoverLink = false;

  let author_name = "";
  let pet_name = "";
  let pet_species = "Chien";
  let years_known = "";
  let message = "";
  let website_url = ""; // Honeypot field for anti-bot
  let form_started_at = Date.now();

  let selectedFile = null;
  let filePreview = null;
  let fileType = null;

  let isSubmitting = false;
  let submitted = false;
  let errorMsg = null;

  const speciesOptions = [
    { value: "Chien", label: "🐶 Chien" },
    { value: "Chat", label: "🐱 Chat" },
    { value: "Autre", label: "✨ Autre compagnon" },
  ];

  onMount(() => {
    form_started_at = Date.now();
  });

  function handleFileChange(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Check size limit (100MB)
    if (file.size > 100 * 1024 * 1024) {
      errorMsg = "Le fichier est trop volumineux (limite max: 100 Mo).";
      return;
    }

    selectedFile = file;
    errorMsg = null;

    if (file.type.startsWith("image/")) {
      fileType = "image";
      filePreview = URL.createObjectURL(file);
    } else if (file.type.startsWith("video/")) {
      fileType = "video";
      filePreview = URL.createObjectURL(file);
    } else {
      fileType = "unknown";
      filePreview = null;
    }
  }

  function removeFile() {
    selectedFile = null;
    filePreview = null;
    fileType = null;
  }

  async function handleSubmit() {
    if (!author_name.trim() || !pet_name.trim() || !message.trim()) {
      errorMsg =
        "Merci de renseigner votre nom, le nom de votre animal et votre message.";
      return;
    }

    isSubmitting = true;
    errorMsg = null;

    try {
      const formData = new FormData();
      formData.append("token", token);
      formData.append("author_name", author_name.trim());
      formData.append("pet_name", pet_name.trim());
      formData.append("pet_species", pet_species);
      formData.append("years_known", years_known.trim());
      formData.append("message", message.trim());
      formData.append("website_url", website_url);
      formData.append("form_started_at", form_started_at.toString());

      if (selectedFile) {
        formData.append("media", selectedFile);
      }

      const res = await fetch("/api/messages/submit", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(
          data.detail || "Une erreur est survenue lors de l'envoi.",
        );
      }

      submitted = true;
      confetti({
        particleCount: 100,
        spread: 80,
        origin: { y: 0.5 },
      });
    } catch (err) {
      errorMsg = err.message;
    } finally {
      isSubmitting = false;
    }
  }

  function resetForm() {
    author_name = "";
    pet_name = "";
    pet_species = "Chien";
    years_known = "";
    message = "";
    selectedFile = null;
    filePreview = null;
    fileType = null;
    submitted = false;
    form_started_at = Date.now();
  }
</script>

<div class="form-page-container">
  <div class="form-wrapper">
    {#if submitted}
      <div class="success-box">
        <div class="success-icon">💌</div>
        <h2>Merci du fond du cœur !</h2>
        <p class="success-lead">
          Votre message pour le <strong>Dr Béatrice Sarda</strong> a bien été transmis.
        </p>
        <p class="success-sub">
          Pour préserver la beauté de ce souvenir, notre équipe relit chaque
          témoignage avant de le glisser définitivement dans son livre d'or.
        </p>
        <div class="success-actions">
          {#if showDiscoverLink && onNavigate}
            <button class="btn btn-primary" on:click={() => onNavigate("home")}>
              <span>📖</span> Découvrir le Livre d'Or
            </button>
          {/if}
          <button class="btn btn-primary" on:click={resetForm}>
            <span>✍️</span> Déposer un autre souvenir
          </button>
        </div>
      </div>
    {:else}
      <div class="form-header">
        <span class="badge-tag">🐾 Retraite du Dr Béatrice Sarda</span>
        <h1>Laissez-lui un message</h1>
        <p>
          Partagez un souvenir, une photo de votre compagnon ou simplement vos
          remerciements pour toutes ces années de bienveillance.
        </p>
      </div>

      {#if errorMsg}
        <div class="error-banner">
          <span>⚠️</span>
          {errorMsg}
        </div>
      {/if}

      <form on:submit|preventDefault={handleSubmit} class="guest-form">
        <!-- Anti-bot honeypot (hidden from humans) -->
        <input
          type="text"
          name="website_url"
          bind:value={website_url}
          class="honeypot"
          tabindex="-1"
          autocomplete="off"
        />

        <div class="form-row">
          <div class="form-group">
            <label for="author"
              >Votre Nom & Prénom <span class="required">*</span></label
            >
            <input id="author" type="text" bind:value={author_name} required />
          </div>

          <div class="form-group">
            <label for="pet"
              >Nom de votre animal <span class="required">*</span></label
            >
            <input id="pet" type="text" bind:value={pet_name} required />
          </div>
        </div>

        <div class="form-group">
          <label for="species">Espèce</label>
          <select id="species" bind:value={pet_species}>
            {#each speciesOptions as opt}
              <option value={opt.value}>{opt.label}</option>
            {/each}
          </select>
        </div>

        <div class="form-group">
          <label for="msg"
            >Votre Message ou Anecdote <span class="required">*</span></label
          >
          <textarea
            id="msg"
            rows="5"
            placeholder="Racontez une anecdote, un moment marquant, ou exprimez votre gratitude au Dr Béatrice Sarda..."
            bind:value={message}
            required
          ></textarea>
        </div>

        <!-- Media Upload -->
        <div class="form-group">
          <label for="media">Ajouter une Photo ou Vidéo (Optionnel)</label>
          <p class="field-hint">
            Une jolie photo de votre animal ou avec le Dr Béatrice Sarda (Haute
            résolution préservée).
          </p>

          {#if !filePreview}
            <div class="upload-dropzone">
              <input
                id="media"
                type="file"
                accept="image/*,video/*"
                on:change={handleFileChange}
                class="file-input"
              />
              <div class="dropzone-content">
                <span class="upload-icon">📷</span>
                <span class="upload-text"
                  ><strong>Cliquez pour choisir un fichier</strong> ou glissez-le
                  ici</span
                >
                <span class="upload-sub"
                  >Photos (JPG, PNG, WEBP) ou courtes vidéos (MP4, MOV)</span
                >
              </div>
            </div>
          {:else}
            <div class="preview-box">
              {#if fileType === "image"}
                <img src={filePreview} alt="Aperçu" class="media-thumb" />
              {:else if fileType === "video"}
                <video src={filePreview} controls class="media-thumb">
                  <track kind="captions" />
                </video>
              {/if}
              <div class="preview-meta">
                <span class="file-name">{selectedFile.name}</span>
                <span class="file-size"
                  >({(selectedFile.size / (1024 * 1024)).toFixed(1)} Mo)</span
                >
                <button
                  type="button"
                  class="btn-remove-file"
                  on:click={removeFile}
                >
                  🗑️ Supprimer cette photo
                </button>
              </div>
            </div>
          {/if}
        </div>

        <button
          type="submit"
          class="btn btn-primary btn-submit"
          disabled={isSubmitting}
        >
          {#if isSubmitting}
            <span class="spinner-small"></span> Envoi de votre souvenir en cours...
          {:else}
            <span>💌</span> Envoyer mon message pour le Dr Béatrice Sarda
          {/if}
        </button>

        <p class="privacy-note">
          🔒 Votre message sera relu et validé par la clinique avant
          d'apparaître dans le livre d'or.
        </p>
      </form>
    {/if}
  </div>
</div>

<style>
  .form-page-container {
    min-height: calc(100vh - 120px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2.5rem 1.5rem;
  }

  .form-wrapper {
    background: #ffffff;
    max-width: 680px;
    width: 100%;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-lg);
    padding: 2.8rem 2.2rem;
  }

  .form-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .badge-tag {
    display: inline-block;
    background: var(--primary-subtle);
    color: var(--primary);
    padding: 0.35rem 0.9rem;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
  }

  .form-header h1 {
    font-size: 2.2rem;
    color: var(--primary);
    margin-bottom: 0.6rem;
  }

  .form-header p {
    color: var(--text-muted);
    font-size: 1.05rem;
  }

  .guest-form {
    display: flex;
    flex-direction: column;
    gap: 1.3rem;
  }

  .honeypot {
    display: none !important;
    visibility: hidden;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.2rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  label {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text-main);
  }

  .required {
    color: #dc2626;
  }

  .field-hint {
    font-size: 0.8rem;
    color: var(--text-subtle);
    margin-top: -0.2rem;
    margin-bottom: 0.3rem;
  }

  input[type="text"],
  select,
  textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background-color: var(--bg-main);
    color: var(--text-main);
    transition:
      border-color var(--transition-fast),
      box-shadow var(--transition-fast);
  }

  input[type="text"]:focus,
  select:focus,
  textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(45, 90, 76, 0.15);
    background-color: #ffffff;
  }

  /* Upload dropzone */
  .upload-dropzone {
    position: relative;
    border: 2px dashed var(--border-subtle);
    border-radius: var(--radius-md);
    background: var(--bg-main);
    padding: 1.5rem;
    text-align: center;
    cursor: pointer;
    transition:
      border-color 0.2s ease,
      background-color 0.2s ease;
  }

  .upload-dropzone:hover {
    border-color: var(--primary);
    background-color: var(--primary-subtle);
  }

  .file-input {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
    width: 100%;
    height: 100%;
  }

  .dropzone-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
  }

  .upload-icon {
    font-size: 1.8rem;
  }

  .upload-text {
    font-size: 0.95rem;
    color: var(--text-main);
  }

  .upload-sub {
    font-size: 0.8rem;
    color: var(--text-subtle);
  }

  /* Preview */
  .preview-box {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: var(--bg-main);
    padding: 0.8rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-subtle);
  }

  .media-thumb {
    width: 80px;
    height: 80px;
    object-fit: cover;
    border-radius: var(--radius-sm);
  }

  .preview-meta {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    flex: 1;
  }

  .file-name {
    font-weight: 600;
    font-size: 0.9rem;
    word-break: break-all;
  }

  .file-size {
    font-size: 0.75rem;
    color: var(--text-subtle);
  }

  .btn-remove-file {
    align-self: flex-start;
    background: none;
    border: none;
    color: #dc2626;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0;
  }

  .btn-submit {
    width: 100%;
    padding: 1rem;
    font-size: 1.05rem;
    margin-top: 0.5rem;
  }

  .btn-submit:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }

  .privacy-note {
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-subtle);
  }

  .error-banner {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    color: #b91c1c;
    padding: 0.8rem 1rem;
    border-radius: var(--radius-sm);
    margin-bottom: 1.2rem;
    font-size: 0.9rem;
  }

  /* Success Screen */
  .success-box {
    text-align: center;
    padding: 2rem 1rem;
  }

  .success-icon {
    font-size: 4rem;
    margin-bottom: 1.2rem;
  }

  .success-box h2 {
    font-size: 2.2rem;
    color: var(--primary);
    margin-bottom: 0.8rem;
  }

  .success-lead {
    font-size: 1.2rem;
    color: var(--text-main);
    margin-bottom: 0.8rem;
  }

  .success-sub {
    font-size: 0.95rem;
    color: var(--text-muted);
    max-width: 480px;
    margin: 0 auto 2rem;
    line-height: 1.5;
  }

  .success-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .spinner-small {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-top-color: #ffffff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    display: inline-block;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 600px) {
    .form-wrapper {
      padding: 1.8rem 1.2rem;
    }
    .form-row {
      grid-template-columns: 1fr;
    }
  }
</style>
