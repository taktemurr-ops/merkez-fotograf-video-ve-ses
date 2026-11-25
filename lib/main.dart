import 'package:flutter/material.dart';
import 'package:medya_motoru/medya_motoru.dart';
import 'package:studio_core/apps/apps.dart';
import 'package:uyg_afis_ve_sosyal_medya_tasarimi/uyg_afis_ve_sosyal_medya_tasarimi.dart';
import 'package:uyg_arka_plan_silme/uyg_arka_plan_silme.dart';
import 'package:uyg_beyaz_gurultu_ve_uyku_sesleri/uyg_beyaz_gurultu_ve_uyku_sesleri.dart';
import 'package:uyg_davetiye_ve_kart_tasarimi/uyg_davetiye_ve_kart_tasarimi.dart';
import 'package:uyg_davul_pedi/uyg_davul_pedi.dart';
import 'package:uyg_dijital_resim_ve_boyama/uyg_dijital_resim_ve_boyama.dart';
import 'package:uyg_dongu_ve_ritim_yapici/uyg_dongu_ve_ritim_yapici.dart';
import 'package:uyg_duvar_kagidi_uretici/uyg_duvar_kagidi_uretici.dart';
import 'package:uyg_ekran_goruntusu_duzenleyici/uyg_ekran_goruntusu_duzenleyici.dart';
import 'package:uyg_filigran_ekleme/uyg_filigran_ekleme.dart';
import 'package:uyg_filtreli_kamera/uyg_filtreli_kamera.dart';
import 'package:uyg_fotograf_bilgisi_silici/uyg_fotograf_bilgisi_silici.dart';
import 'package:uyg_fotograf_duzenleyici/uyg_fotograf_duzenleyici.dart';
import 'package:uyg_fotograf_iyilestirme/uyg_fotograf_iyilestirme.dart';
import 'package:uyg_fotograf_renklendirme/uyg_fotograf_renklendirme.dart';
import 'package:uyg_fotograf_sikistirma/uyg_fotograf_sikistirma.dart';
import 'package:uyg_gif_yapici/uyg_gif_yapici.dart';
import 'package:uyg_gorselden_pdf/uyg_gorselden_pdf.dart';
import 'package:uyg_gurultu_azaltma/uyg_gurultu_azaltma.dart';
import 'package:uyg_kirp_ve_boyutlandir/uyg_kirp_ve_boyutlandir.dart';
import 'package:uyg_kolaj/uyg_kolaj.dart';
import 'package:uyg_kopya_fotograf_bulucu/uyg_kopya_fotograf_bulucu.dart';
import 'package:uyg_logo_tasarimi/uyg_logo_tasarimi.dart';
import 'package:uyg_meme_yapici/uyg_meme_yapici.dart';
import 'package:uyg_muzik_calar/uyg_muzik_calar.dart';
import 'package:uyg_otomatik_altyazi/uyg_otomatik_altyazi.dart';
import 'package:uyg_piksel_sanati_editoru/uyg_piksel_sanati_editoru.dart';
import 'package:uyg_piyano/uyg_piyano.dart';
import 'package:uyg_podcast_kaydi/uyg_podcast_kaydi.dart';
import 'package:uyg_sentezleyici/uyg_sentezleyici.dart';
import 'package:uyg_ses_degistirici/uyg_ses_degistirici.dart';
import 'package:uyg_ses_duzenleyici/uyg_ses_duzenleyici.dart';
import 'package:uyg_ses_formati_donusturucu/uyg_ses_formati_donusturucu.dart';
import 'package:uyg_ses_yukseltici/uyg_ses_yukseltici.dart';
import 'package:uyg_slayt_gosterisi_video/uyg_slayt_gosterisi_video.dart';
import 'package:uyg_video_hiz/uyg_video_hiz.dart';
import 'package:uyg_video_kirp_ve_birlestir/uyg_video_kirp_ve_birlestir.dart';
import 'package:uyg_video_sikistirma/uyg_video_sikistirma.dart';
import 'package:uyg_videodan_ses_cikarma/uyg_videodan_ses_cikarma.dart';
import 'package:uyg_yuz_ve_plaka_bulaniklastirma/uyg_yuz_ve_plaka_bulaniklastirma.dart';
import 'package:uyg_zaman_atlamali_video/uyg_zaman_atlamali_video.dart';
import 'package:uyg_zil_sesi_yapici/uyg_zil_sesi_yapici.dart';
import 'package:uyg_video_oynatici/uyg_video_oynatici.dart';
import 'package:uyg_gizli_album/uyg_gizli_album.dart';
import 'package:uyg_ekran_kaydedici/uyg_ekran_kaydedici.dart';

/// Fotoğraf, Video ve Ses: 45 araç tek uygulamada. Çoğu internetsiz ve
/// cihazda çalışır; her aracın verisi ayrı saklanır; reklam yalnızca bir
/// araçtan çıkarken ve en az 3 dakika arayla gösterilir.
final hubConfig = AppHubConfig(
  hubId: 'merkez-fotograf-video-ve-ses',
  title: medyaHubTitle,
  tagline: medyaHubTagline,
  icon: Icons.perm_media_rounded,
  style: medyaHubStyle,
  categories: medyaCategories,
  tools: [
    fotografDuzenleyiciTool,
    kolajTool,
    kirpVeBoyutlandirTool,
    arkaPlanSilmeTool,
    fotografSikistirmaTool,
    videoKirpVeBirlestirTool,
    gifYapiciTool,
    filigranEklemeTool,
    memeYapiciTool,
    gorseldenPdfTool,
    muzikCalarTool,
    zilSesiYapiciTool,
    sesDuzenleyiciTool,
    beyazGurultuVeUykuSesleriTool,
    davulPediTool,
    piyanoTool,
    sesDegistiriciTool,
    duvarKagidiUreticiTool,
    filtreliKameraTool,
    slaytGosterisiVideoTool,
    videoSikistirmaTool,
    videoHizTool,
    videodanSesCikarmaTool,
    otomatikAltyaziTool,
    fotografRenklendirmeTool,
    fotografIyilestirmeTool,
    yuzVePlakaBulaniklastirmaTool,
    fotografBilgisiSiliciTool,
    kopyaFotografBulucuTool,
    zamanAtlamaliVideoTool,
    ekranGoruntusuDuzenleyiciTool,
    pikselSanatiEditoruTool,
    dijitalResimVeBoyamaTool,
    logoTasarimiTool,
    davetiyeVeKartTasarimiTool,
    afisVeSosyalMedyaTasarimiTool,
    podcastKaydiTool,
    sesYukselticiTool,
    gurultuAzaltmaTool,
    sesFormatiDonusturucuTool,
    donguVeRitimYapiciTool,
    sentezleyiciTool,
    videoOynaticiTool,
    gizliAlbumTool,
    ekranKaydediciTool,
  ],
  featured: medyaFeatured,
  privacyUrl: 'https://github.com/taktemurr-ops/merkez-fotograf-video-ve-ses/blob/main/PRIVACY.md',
);

void main() => bootstrapAppHub(hubConfig);
