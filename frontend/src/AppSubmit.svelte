<script>
  import { onMount } from "svelte";
  import SubmitForm from "./lib/SubmitForm.svelte";

  // Clé par défaut (secours hors-ligne)
  const DEFAULT_SLUG = "souvenir-v7k9x4p";

  // Token technique interne frontend <-> backend
  const BACKEND_SUBMIT_TOKEN = "retraitebs-7x8k2q";

  let isAuthorized = false;
  let isChecking = true;
  let manualKey = "";
  let manualKeyError = false;

  function extractCandidateSlug() {
    if (typeof window === "undefined") return "";

    // 1. Pathname
    const rawPath = window.location.pathname.replace(/^\/+|\/+$/g, "").trim();
    const pathParts = rawPath.split("/").filter(Boolean);

    // 2. Hash
    const rawHash = window.location.hash.replace(/^#\/?/, "").trim();
    const hashParts = rawHash.split("/").filter(Boolean);

    // 3. Query param
    const urlParams = new URLSearchParams(window.location.search);
    const queryKey = (
      urlParams.get("cle") ||
      urlParams.get("key") ||
      urlParams.get("token") ||
      ""
    ).trim();

    return queryKey || pathParts[0] || hashParts[0] || rawPath || rawHash || "";
  }

  async function checkAuthorization() {
    if (typeof window === "undefined") return;

    const candidate = extractCandidateSlug();

    if (!candidate) {
      isAuthorized = false;
      isChecking = false;
      return;
    }

    try {
      const res = await fetch(
        `/api/client-access/verify?slug=${encodeURIComponent(candidate)}`,
      );
      if (res.ok) {
        const data = await res.json();
        isAuthorized = !!data.valid;
      } else {
        // Fallback local si backend hors ligne
        isAuthorized = candidate.toLowerCase() === DEFAULT_SLUG.toLowerCase();
      }
    } catch (e) {
      isAuthorized = candidate.toLowerCase() === DEFAULT_SLUG.toLowerCase();
    } finally {
      isChecking = false;
      manualKeyError = false;
    }
  }

  async function handleManualUnlock() {
    const input = manualKey.trim().replace(/^#\/?/, "").replace(/^\/+/, "");
    if (!input) return;

    try {
      const res = await fetch(
        `/api/client-access/verify?slug=${encodeURIComponent(input)}`,
      );
      if (res.ok) {
        const data = await res.json();
        if (data.valid) {
          window.history.pushState({}, "", `/${input}`);
          isAuthorized = true;
          manualKeyError = false;
          return;
        }
      } else if (input.toLowerCase() === DEFAULT_SLUG.toLowerCase()) {
        window.history.pushState({}, "", `/${input}`);
        isAuthorized = true;
        manualKeyError = false;
        return;
      }
    } catch (e) {
      if (input.toLowerCase() === DEFAULT_SLUG.toLowerCase()) {
        window.history.pushState({}, "", `/${input}`);
        isAuthorized = true;
        manualKeyError = false;
        return;
      }
    }

    manualKeyError = true;
  }

  onMount(() => {
    checkAuthorization();
    window.addEventListener("hashchange", checkAuthorization);
    window.addEventListener("popstate", checkAuthorization);
    return () => {
      window.removeEventListener("hashchange", checkAuthorization);
      window.removeEventListener("popstate", checkAuthorization);
    };
  });
</script>

<div class="app-root">
  <header class="client-navbar">
    <div class="nav-container">
      <div class="brand">
        <span class="brand-icon">🐾</span>
        <div class="brand-text">
          <span class="brand-title">Livre d'Or — Dr Béatrice Sarda</span>
          <span class="brand-sub">Clinique Vetalians</span>
        </div>
      </div>
      <div class="client-badge">
        <span>💌 Espace Témoignages</span>
      </div>
    </div>
  </header>

  <main class="view-content">
    {#if isAuthorized}
      <SubmitForm token={BACKEND_SUBMIT_TOKEN} showDiscoverLink={false} />
    {:else}
      <div class="locked-container">
        <div class="locked-card">
          <div class="lock-icon">🔒</div>
          <h2>Espace Privé</h2>
          <p class="lock-desc">
            Pour préserver la surprise du départ en retraite du <strong
              >Dr Béatrice Sarda</strong
            >, cet espace de dépôt est accessible
            <strong>exclusivement sur invitation</strong>.
          </p>
          <div class="info-tip">
            <span class="tip-icon">💡</span>
            <p>
              Veuillez utiliser le lien direct ou scanner le <strong
                >QR Code</strong
              > qui vous a été transmis par l'équipe de la clinique.
            </p>
          </div>

          <form
            class="unlock-box"
            on:submit|preventDefault={handleManualUnlock}
          >
            <label for="invite-code"
              >Vous disposez d'une clé d'invitation ?</label
            >
            <div class="input-row">
              <input
                id="invite-code"
                type="text"
                bind:value={manualKey}
                class:input-error={manualKeyError}
              />
              <button type="submit" class="btn-unlock">Accéder</button>
            </div>
            {#if manualKeyError}
              <p class="error-text">
                ⚠️ Clé d'accès non reconnue. Merci de vérifier le lien reçu.
              </p>
            {/if}
          </form>
        </div>
      </div>
    {/if}
  </main>

  <footer class="client-footer">
    <div class="footer-inner">
      <p>
        Merci pour votre témoignage et votre confiance au fil des années !
        🐶🐱✨
      </p>
    </div>
  </footer>
</div>

<style>
  .app-root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--bg-main, #fdfbf7);
  }

  .client-navbar {
    background: #ffffff;
    border-bottom: 1px solid var(--border-subtle, #ede7df);
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow-sm, 0 2px 8px rgba(44, 62, 80, 0.05));
  }

  .nav-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0.9rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 0.8rem;
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
    font-size: 1.15rem;
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

  .client-badge {
    background: var(--primary-subtle, #f0f7f3);
    color: var(--primary, #2d5a43);
    padding: 0.35rem 0.8rem;
    border-radius: var(--radius-full, 9999px);
    font-size: 0.82rem;
    font-weight: 600;
  }

  .view-content {
    flex: 1;
    padding: 1.5rem 1rem 3rem;
  }

  /* Locked Container */
  .locked-container {
    min-height: calc(100vh - 200px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
  }

  .locked-card {
    background: #ffffff;
    max-width: 540px;
    width: 100%;
    border-radius: 16px;
    border: 1px solid var(--border-subtle, #ede7df);
    box-shadow: 0 10px 30px rgba(44, 62, 80, 0.08);
    padding: 2.5rem 2rem;
    text-align: center;
  }

  .lock-icon {
    font-size: 3.2rem;
    margin-bottom: 1rem;
  }

  .locked-card h2 {
    font-family: var(--font-serif, Georgia, serif);
    font-size: 1.7rem;
    color: var(--primary, #2d5a43);
    margin-bottom: 0.8rem;
  }

  .lock-desc {
    color: var(--text-muted, #7c8a82);
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  .info-tip {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    background: var(--primary-subtle, #f0f7f3);
    border: 1px solid rgba(45, 90, 67, 0.15);
    border-radius: 12px;
    padding: 1rem;
    text-align: left;
    margin-bottom: 2rem;
  }

  .tip-icon {
    font-size: 1.3rem;
  }

  .info-tip p {
    font-size: 0.9rem;
    color: var(--primary, #2d5a43);
    line-height: 1.45;
    margin: 0;
  }

  .unlock-box {
    border-top: 1px solid var(--border-subtle, #ede7df);
    padding-top: 1.5rem;
    text-align: left;
  }

  .unlock-box label {
    display: block;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-main, #2c3e50);
    margin-bottom: 0.6rem;
  }

  .input-row {
    display: flex;
    gap: 0.6rem;
  }

  .input-row input {
    flex: 1;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    border: 1px solid var(--border-subtle, #ede7df);
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s ease;
  }

  .input-row input:focus {
    border-color: var(--primary, #2d5a43);
    box-shadow: 0 0 0 3px rgba(45, 90, 67, 0.1);
  }

  .input-row input.input-error {
    border-color: #e53e3e;
    background-color: #fff5f5;
  }

  .btn-unlock {
    background: var(--primary, #2d5a43);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.3rem;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: opacity 0.2s ease;
  }

  .btn-unlock:hover {
    opacity: 0.9;
  }

  .error-text {
    font-size: 0.85rem;
    color: #e53e3e;
    margin-top: 0.5rem;
  }

  .client-footer {
    background: #ffffff;
    border-top: 1px solid var(--border-subtle, #ede7df);
    padding: 1.5rem;
    margin-top: auto;
  }

  .footer-inner {
    max-width: 900px;
    margin: 0 auto;
    text-align: center;
    font-size: 0.88rem;
    color: var(--text-muted, #7c8a82);
  }

  @media (max-width: 650px) {
    .client-badge {
      display: none;
    }
    .locked-card {
      padding: 1.8rem 1.3rem;
    }
  }
</style>
