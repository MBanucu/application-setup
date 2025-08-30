{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python3.withPackages (
      ps: with ps; [
        pytz
        weasyprint
        distutils
        pandas
      ]
    ))
    pkgs.texliveFull
    pkgs.pdftk
    pkgs.xfce.xfce4-terminal
    pkgs.wget
    pkgs.unzip
  ];

  shellHook = ''
    # if "kpsewhich uarial.sty" is not found, run this script to install the URW Arial font
    if ! kpsewhich uarial.sty; then
      echo "Installing URW Arial font..."
      ${pkgs.wget}/bin/wget https://mirror.ctan.org/fonts/urw/arial.zip
      unzip arial.zip
      mkdir -p ~/texmf/tex/latex/uarial
      mkdir -p ~/texmf/fonts/afm/urw/arial
      mkdir -p ~/texmf/fonts/tfm/urw/arial
      mkdir -p ~/texmf/fonts/type1/urw/arial
      mkdir -p ~/texmf/fonts/vf/urw/arial
      mkdir -p ~/texmf/fonts/map/dvips/uarial

      cp arial/latex/* ~/texmf/tex/latex/uarial/
      cp arial/afm/* ~/texmf/fonts/afm/urw/arial/
      cp arial/tfm/* ~/texmf/fonts/tfm/urw/arial/
      cp arial/type1/* ~/texmf/fonts/type1/urw/arial/
      cp arial/vf/* ~/texmf/fonts/vf/urw/arial/
      cp arial/map/* ~/texmf/fonts/map/dvips/uarial/

      mktexlsr ~/texmf
      updmap-user --enable Map=ua1.map
      updmap-user

      rm -r arial
      rm arial.zip
    fi
  '';
}
