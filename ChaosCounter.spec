# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['1080ptest.py'],
             pathex=['ENTER PATH TO main.py HERE'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

a.datas += [('StartWindowBackground.png','ENTER PATH HERE', 'Data'),
('StartButtonBackground.png','ENTER PATH HERE', 'Data'),
('CloseButtonBackground.png','ENTER PATH HERE', 'Data'),
('ComboBoxBackground.png','ENTER PATH HERE', 'Data'),
('InfoButton.png','ENTER PATH HERE', 'Data'),
('Empty.png','ENTER PATH HERE', 'Data'),
('OrbofAlteration.png','ENTER PATH HERE', 'Data'),
('OrbofFusing.png','ENTER PATH HERE', 'Data'),
('OrbofAlchemy.png','ENTER PATH HERE', 'Data'),
('ChaosOrb.png','ENTER PATH HERE', 'Data'),
('ChromaticOrb.png','ENTER PATH HERE', 'Data'),
('JewellersOrb.png','ENTER PATH HERE', 'Data'),
('OrbofChance.png','ENTER PATH HERE', 'Data'),
('CartographersChisel.png','ENTER PATH HERE', 'Data'),
('OrbofScouring.png','ENTER PATH HERE', 'Data'),
('BlessedOrb.png','ENTER PATH HERE', 'Data'),
('RegalOrb.png','ENTER PATH HERE', 'Data'),
('VaalOrb.png','ENTER PATH HERE', 'Data'),
('SacrificeatDusk.png','ENTER PATH HERE', 'Data'),
('SacrificeatMidnight.png','ENTER PATH HERE', 'Data'),
('SacrificeatDawn.png','ENTER PATH HERE', 'Data'),
('SacrificeatNoon.png','ENTER PATH HERE', 'Data'),
('MortalGrief.png','ENTER PATH HERE', 'Data'),
('MortalRage.png','ENTER PATH HERE', 'Data'),
('MortalHope.png','ENTER PATH HERE', 'Data'),
('MortalIgnorance.png','ENTER PATH HERE', 'Data'),
('OfferingtotheGoddess.png','ENTER PATH HERE', 'Data'),
('SimpleSextant.png','ENTER PATH HERE', 'Data'),
('PrimeSextant.png','ENTER PATH HERE', 'Data'),
('AwakenedSextant.png','ENTER PATH HERE', 'Data'),
('OrbofHorizons.png','ENTER PATH HERE', 'Data'),
('SilverCoin.png','ENTER PATH HERE', 'Data'),
('refEmpty.png','ENTER PATH HERE', 'Data'),
('refOrbofAlteration.png','ENTER PATH HERE', 'Data'),
('refOrbofFusing.png','ENTER PATH HERE', 'Data'),
('refOrbofAlchemy.png','ENTER PATH HERE', 'Data'),
('refChaosOrb.png','ENTER PATH HERE', 'Data'),
('refChromaticOrb.png','ENTER PATH HERE', 'Data'),
('refJewellersOrb.png','ENTER PATH HEREg', 'Data'),
('refOrbofChance.png','ENTER PATH HERE', 'Data'),
('refCartographersChisel.png','ENTER PATH HERE', 'Data'),
('refOrbofScouring.png','ENTER PATH HERE', 'Data'),
('refBlessedOrb.png','ENTER PATH HERE', 'Data'),
('refRegalOrb.png','ENTER PATH HERE', 'Data'),
('refVaalOrb.png','ENTER PATH HERE', 'Data'),
('refSacrificeatDusk.png','ENTER PATH HERE', 'Data'),
('refSacrificeatMidnight.png','ENTER PATH HERE', 'Data'),
('refSacrificeatDawn.png','ENTER PATH HERE', 'Data'),
('refSacrificeatNoon.png','ENTER PATH HERE', 'Data'),
('refMortalGrief.png','ENTER PATH HERE', 'Data'),
('refMortalRage.png','ENTER PATH HERE', 'Data'),
('refMortalHope.png','ENTER PATH HERE', 'Data'),
('refMortalIgnorance.png','ENTER PATH HERE', 'Data'),
('refOfferingtotheGoddess.png','ENTER PATH HERE', 'Data'),
('refSimpleSextant.png','ENTER PATH HERE', 'Data'),
('refPrimeSextant.png','ENTER PATH HERE', 'Data'),
('refAwakenedSextant.png','ENTER PATH HERE', 'Data'),
('refOrbofHorizons.png','ENTER PATH HERE', 'Data'),
('refSilverCoin.png','ENTER PATH HERE', 'Data'),
('OverlayBackground.png','ENTER PATH HERE', 'Data'),
('SettingsButton.png','ENTER PATH HERE', 'Data'),
('RefreshButton.png','ENTER PATH HERE', 'Data'),
('OkButton.png','ENTER PATH HERE', 'Data'),
('DonateWindowBackground.png','ENTER PATH HERE', 'Data'),
('PayPalButton.png','ENTER PATH HERE', 'Data'),
('GitHubButton.png','ENTER PATH HERE', 'Data'),
('CCIcon.png','ENTER PATH HERE', 'Data')]


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='1080ptest',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)