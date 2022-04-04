rm infrastructure/functions/*.zip
for i in functions/*; do
  pushd ${i}
  TIMESTAMP=$(git ls-files -z . | xargs -0 -n1 -I{} -- git log -1 --date=format:"%Y%m%d%H%M" --format="%ad" {} | sort -r | head -n 1)
  find . -exec touch -t $TIMESTAMP {} +
  folder=$(basename ${i})
  find -L . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
  zip -rX "${folder}.zip" ./;
  touch -t $TIMESTAMP "${folder}.zip"
  mv "${folder}.zip" ../
  popd
mv ./functions/*.zip ./infrastructure/functions
done
