import numpy as np


def make_loading_case(seed, tones=64, taps=8, noise_var=0.1, pilots=20):
    """
    Generate one synthetic DMT channel.

    Inputs:
        seed      : int, random seed (same seed -> same channel)
        tones     : int, number of tones N
        taps      : int, number of multipath channel taps
        noise_var : float, noise variance per tone
        pilots    : int, number of pilot / noise-only observations averaged

    Returns:
        g_true : array (tones,), |h|^2 / noise_var (ideal channel knowledge)
        g_hat  : array (tones,), estimate from noisy pilots and a noise-only
                 calibration (realistic channel knowledge), floored at 1e-12
    """
    rng = np.random.default_rng(seed)
    power = np.exp(-np.arange(taps) / 2.0)
    power /= power.sum()
    channel_taps = np.sqrt(power / 2) * (
        rng.normal(size=taps) + 1j * rng.normal(size=taps))
    h = np.fft.fft(channel_taps, n=tones)
    noise = np.sqrt(noise_var / 2) * (
        rng.normal(size=(pilots, tones)) + 1j * rng.normal(size=(pilots, tones)))
    h_hat = (h[None, :] + noise).mean(axis=0)
    noise_only = np.sqrt(noise_var / 2) * (
        rng.normal(size=(pilots, tones)) + 1j * rng.normal(size=(pilots, tones)))
    variance_hat = np.mean(np.abs(noise_only) ** 2, axis=0)
    g_true = np.abs(h) ** 2 / noise_var
    g_hat = np.abs(h_hat) ** 2 / np.maximum(variance_hat, 1e-12)
    return g_true, np.maximum(g_hat, 1e-12)