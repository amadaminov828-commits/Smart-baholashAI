$env:Path = "C:\Program Files\nodejs;" + $env:Path
npx -y create-next-app@latest frontend --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm
